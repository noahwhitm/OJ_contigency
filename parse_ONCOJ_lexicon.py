import sys, csv, xml.etree.ElementTree

# xml_file = "data/data-release/lexicon.xml"
                
def grab2args(default1,default2=None):
   arg1 = sys.argv[1].strip('"').strip("'") if len(sys.argv) > 1 else default1
   arg2 = sys.argv[2].strip('"').strip("'") if len(sys.argv) > 2 else default2
   if isinstance(default1,int): arg1 = int(arg1)
   if isinstance(default2,int): arg2 = int(arg2)
   return arg1,arg2

def xml_to_csv(xml_file, csv_file):
    tree = xml.etree.ElementTree.parse(xml_file)
    root = tree.getroot()
    headers, cols=[], []
    for superchild in root:
        for child in superchild:
            headers, cols = [{ "superchild: ", root.atrributes}],[]
            headers.appaned(subnode.tag)
            row.append(subnode.text)
                # data_rows.append(row.copy())
    
        print(headers)
        # print(cols)
    # csvwriter = csv.writer(csvfile)
    # header, data_rows = [], [
    # child in root:
    # with open(csv_file, 'w', newline='') as csvfile:
    


if __name__ == "__main__":
    xml_file,csv_file = grab2args('data/data-release/lexicon.xml')
    xml_to_csv(xml_file, csv_file)
    print(f"XML to CSV conversion completed. CSV file saved as {csv_file}")

  