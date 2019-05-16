using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Data2SQL
{
    public class SQLHandler
    {
        private SqlCommand command;
        private string connectionString = "Server=tcp:deepbroccoliserver.database.windows.net,1433;Initial Catalog=DeepBroccoliDatabase;Persist Security Info=False;User ID=azzureFunction;Password=brokkoli_2019;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;";
        private SqlConnection conn;


        public SQLHandler()
        {
            this.conn = new SqlConnection(connectionString);
        }

        public bool OpenConnection()
        {
            try
            {
                this.conn.Open();
                return true;
            }catch(Exception e)
            {
                Console.WriteLine($"not able to open connection: {e.ToString()}");
                return false;
            }
        }

        public void CloseConnection()
        {
            conn.Close();
        }

        public bool WriteToSQL(List<Dictionary<string, string>> csvData)
        {
            try
            {
                foreach (var broccoliValue in csvData)
                {
                    bool isInDatabase = false;
                    if (broccoliValue.TryGetValue("id", out var id) && broccoliValue.TryGetValue("lat", out var lat) && broccoliValue.TryGetValue("long", out var longitude))
                    {
                        Console.WriteLine("id, lat and long are available");
                        this.command = new SqlCommand("select * from dbo.broccoli where id=@id and lat=@lat and long=@long;", conn);
                        this.AddWithValue("id", id);
                        this.AddWithValue("lat", lat);
                        this.AddWithValue("long", longitude);
                        using (SqlDataReader reader = command.ExecuteReader())
                        {
                            Console.WriteLine("check if id, lat and long are in database");
                            while (reader.Read())
                            {
                                var idSQL = reader["id"].ToString();
                                var latSQL = reader["lat"].ToString();
                                var longSQL = reader["long"].ToString();

                                if (idSQL.Equals(id) && latSQL.Equals(lat) && longSQL.Equals(longitude))
                                {
                                    Console.WriteLine("id, lat and long are in database");
                                    isInDatabase = true;
                                    break;
                                }

                            }
                        }
                        if (!isInDatabase)
                        {
                            Console.WriteLine("id, lat and long are not in database, but will be inserted into database");
                            // ad new broccoli
                            this.command = new SqlCommand("insert into dbo.broccoli (id, lat, long) values (@id, @lat, @long);", conn);
                            this.AddWithValue("id", id);
                            this.AddWithValue("lat", lat);
                            this.AddWithValue("long", longitude);
                            command.ExecuteNonQuery();

                        }
                        //check if row was already inserted
                        this.command = new SqlCommand("select broccolivalues.timestamp, broccolivalues.id " +
                            "from broccoli inner join broccolivalues on broccoli.id = @id; ", conn);
                        this.AddWithValue("id", id);
                        var update = false;
                        using (SqlDataReader reader = command.ExecuteReader())
                        {
                            while (reader.Read())
                            {
                                var timestampSQL = Convert.ToDateTime(reader["timestamp"].ToString());
                                var idSQL = reader["id"].ToString();
                                if (broccoliValue.TryGetValue("timestamp", out var timestamp) && DateTime.Compare(Convert.ToDateTime(timestamp), timestampSQL) == 0 && idSQL.Equals(id))
                                {
                                    update = true;
                                    break;
                                }

                            }
                        }
                        if (update)
                        {
                            //create update command
                            this.command = new SqlCommand("UPDATE dbo.broccolivalues SET id = @id, timestamp = @timestamp, pixelCount = @pixelCount," +
                                "maxNDVI = @maxNDVI, minNDVI = @minNDVI, meanNDVI = @meanNDVI, medianNDVI = @medianNDVI, maxNDRE = @maxNDRE," +
                                "minNDRE = @minNDRE, meanNDRE = @meanNDRE, medianNDRE =@medianNDRE, NDVI_15_Quantile = @NDVI_15_Quantile, " +
                                "NDVI_25_Quantile = @NDVI_25_Quantile, NDVI_75_Quantile = @NDVI_75_Quantile, NDVI_85_Quantile = @NDVI_85_Quantile,"+
                                "NDRE_15_Quantile = @NDRE_15_Quantile, NDRE_25_Quantile = @NDRE_25_Quantile, NDRE_75_Quantile = @NDRE_75_Quantile, NDRE_85_Quantile = @NDRE_85_Quantile "+
                                "WHERE timestamp=@timestamp and id=@id;", conn);
                        }
                        else
                        {
                            // create command to insert values
                            this.command = new SqlCommand("insert into dbo.broccolivalues(id, timestamp, pixelCount, maxNDVI, minNDVI, " +
                                "meanNDVI, medianNDVI, maxNDRE, minNDRE, meanNDRE, medianNDRE, NDVI_15_Quantile, NDVI_25_Quantile, NDVI_75_Quantile, NDVI_85_Quantile,"+
                                "NDRE_15_Quantile, NDRE_25_Quantile, NDRE_75_Quantile, NDRE_85_Quantile) values (@id, @timestamp, @pixelCount , @maxNDVI," +
                                "@minNDVI, @meanNDVI, @medianNDVI, @maxNDRE, @minNDRE, @meanNDRE, @medianNDRE, @NDVI_15_Quantile, @NDVI_25_Quantile, @NDVI_75_Quantile, @NDVI_85_Quantile, "+
                                "@NDRE_15_Quantile, @NDRE_25_Quantile, @NDRE_75_Quantile, @NDRE_85_Quantile) " +
                                "select id from dbo.broccoli where id=@id;", conn);
                        }

                        this.AddWithValue("id", broccoliValue["id"]);
                        this.AddWithValue("timestamp", broccoliValue["timestamp"]);
                        this.AddWithValue("pixelCount", broccoliValue["pixelCount"]);
                        this.AddWithValue("maxNDVI", broccoliValue["maxNDVI"]);
                        this.AddWithValue("minNDVI", broccoliValue["minNDVI"]);
                        this.AddWithValue("meanNDVI", broccoliValue["meanNDVI"]);
                        this.AddWithValue("medianNDVI", broccoliValue["medianNDVI"]);
                        this.AddWithValue("maxNDRE", broccoliValue["maxNDRE"]);
                        this.AddWithValue("minNDRE", broccoliValue["minNDRE"]);
                        this.AddWithValue("meanNDRE", broccoliValue["meanNDRE"]);
                        this.AddWithValue("medianNDRE", broccoliValue["medianNDRE"]);
                        this.AddWithValue("NDVI_15_Quantile", broccoliValue["NDVI_15_Quantile"]);
                        this.AddWithValue("NDVI_25_Quantile", broccoliValue["NDVI_25_Quantile"]);
                        this.AddWithValue("NDVI_75_Quantile", broccoliValue["NDVI_75_Quantile"]);
                        this.AddWithValue("NDVI_85_Quantile", broccoliValue["NDVI_85_Quantile"]);
                        this.AddWithValue("NDRE_15_Quantile", broccoliValue["NDRE_15_Quantile"]);
                        this.AddWithValue("NDRE_25_Quantile", broccoliValue["NDRE_25_Quantile"]);
                        this.AddWithValue("NDRE_75_Quantile", broccoliValue["NDRE_75_Quantile"]);
                        this.AddWithValue("NDRE_85_Quantile", broccoliValue["NDRE_85_Quantile"]);
                        command.ExecuteNonQuery();
                    }
                }
                return true;
            }
            catch(Exception e)
            {
                Console.WriteLine($"Error: {e.ToString()}");
                return false;
            }
            
        }

        private void AddWithValue(string key, string value)
        {
            if (value == string.Empty)
            {
                this.command.Parameters.AddWithValue($"@{key}", DBNull.Value);
            }
            else
            {
                this.command.Parameters.AddWithValue($"@{key}", value);
            }
        }

    }
}
