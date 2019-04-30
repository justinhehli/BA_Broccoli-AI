using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Data2SQL
{
    class Program
    {
        static void Main(string[] args)
        {
            List<string> csvFiles = new List<string>();
            if (args[0].EndsWith("txt"))
            {
                using (var reader = new StreamReader(args[0]))
                {
                    while (!reader.EndOfStream)
                    {
                        var line = reader.ReadLine();
                        if (line.EndsWith("csv"))
                        {
                            csvFiles.Add(line);
                        }
                    }
                }
            }
            else if (args[0].EndsWith("csv"))
            {
                csvFiles.Add(args[0]);
            }
            var sqlHandler = new SQLHandler();
            if (sqlHandler.OpenConnection())
            {
                foreach (var csvFile in csvFiles)
                {
                    var reader = new CSVreader();
                    var listToAdd = reader.readCSV(csvFile);
                    sqlHandler.WriteToSQL(listToAdd);
                }
            }
            else
            {
                Console.WriteLine("Not able to open connection");
            }
            sqlHandler.CloseConnection();
        }
    }
}
