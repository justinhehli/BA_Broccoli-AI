using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Data2SQL
{
    public class CSVreader
    { 
        private List<string> valueNames = new List<string>();
        private List<Dictionary<string, string>> broccoliValues = new List<Dictionary<string, string>>();



        public List<Dictionary<string,string>> readCSV(string fileToRead)
        {
            using (var reader = new StreamReader(fileToRead))
            {
                bool firstLine = true;
                while (!reader.EndOfStream)
                {
                    var valueDictionary = new Dictionary<string, string>();
                    var line = reader.ReadLine();
                    var values = line.Split(';');
                    if (firstLine)
                    {
                        foreach(var value in values)
                        {
                            valueNames.Add(value);
                        }
                        firstLine = false;
                    }
                    else
                    {
                        var counter = 0;
                        foreach (var value in values)
                        { 
                            valueDictionary.Add(valueNames[counter], value);
                            counter++;
                        }
                        this.broccoliValues.Add(valueDictionary);
                    }
                }
            }
            return broccoliValues;
        }
    }
}
