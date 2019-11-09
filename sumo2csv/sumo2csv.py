# sumo2csv.py
# Author: Quentin Goss
# Generates a csv file of sumo network data
import pantherine as purr
import math

def main():
    map_dir = "../orlando-seg1/"
    
    # Load Nodes
    nod_xml = purr.mrf(map_dir,r'*.nod.xml')
    nodes = purr.readXMLtag(nod_xml,'node')
    
    # Load Edges
    edg_xml = purr.mrf(map_dir,r'*edg.xml')
    edges = purr.readXMLtag(edg_xml,'edge')
    
    # Correlate From/To Nodes with edges
    print('Finding Nodes From')
    nids_from = [edge['from'] for edge in edges]
    nodes_from = purr.flattenlist(purr.batchfilterdicts(nodes,'id',nids_from,show_progress=True))
    
    print('\nFinding Nodes To')
    nids_to = [edge['to'] for edge in edges]
    nodes_to = purr.flattenlist(purr.batchfilterdicts(nodes,'id',nids_to,show_progress=True))
    print()
    
    # Create the CSV for Nodes
    node_attr = ['id','x','y','z','type','tlType','tl','radius','keepClear','rightOfWay']
    node_csv = 'node.csv'
    with open(node_csv,'w') as csv:
        # Column Names
        csv.write(node_attr[0])
        for attr in node_attr[1:]:
            csv.write(',%s' % (attr))
        csv.write('\n')
        
        # Fill in rows
        n = 0; total = len(nodes)
        for node in nodes:
            csv.write(node[node_attr[0]])
            for attr in node_attr[1:]:
                csv.write(',')
                try:
                    csv.write(node[attr])
                except KeyError:
                    pass
                csv.write('\n')
                continue
            n+=1;purr.update(n,total, msg="Writing node.csv ")
            continue
        pass
    
    print()
    
    # Create the CSV for Edges
    edge_attr = ['id','from','to','type','numLanes','speed','priority','spreadType','width','name','endOffset','sidewalkWidth']
    edge_allow = ['emergency','authority','passenger','hov','taxi','bus','delivery','truck','trailer','motorcyle','moped']
    edge_csv = 'edge.csv'
    with open(edge_csv,'w') as csv:
        # Column Names
        csv.write(edge_attr[0])
        for attr in edge_attr[1:]:
            csv.write(',%s' % (attr))
        csv.write(',length')
        for attr in edge_allow:
            csv.write(',%s' % (attr))
        csv.write('\n')
        
        # Fill in Rows
        n = 0; total = len(edges)
        for i, edge in enumerate(edges):
            # id
            csv.write(edge[edge_attr[0]])
            
            # Attributes
            for attr in edge_attr[1:]:
                csv.write(',')
                try:
                    csv.write(edge[attr])
                except KeyError:
                    pass
                continue
                
            # Length
            try:
                csv.write(',%.3f' % (shape_len(edge['shape'])))
            except KeyError:
                x0 = float(nodes_from[i]['x'])
                y0 = float(nodes_from[i]['y'])
                x1 = float(nodes_to[i]['x'])
                y1 = float(nodes_to[i]['y'])
                csv.write(',%.3f' % (dist(x0,y0,x1,y1)))
            
            # Vehicle Types
            vtype_allowed = [0 for item in edge_allow]
            
            # Has neither tag. It is assumed that all vehicles are allowed.
            if (not purr.xml_has_atrribute(edge,'allow')) and (not purr.xml_has_atrribute(edge,'disallow')):
                vtype_allowed = [1 for item in edge_allow]
            
            # Has the allow tag. Those specified are allowed
            elif (purr.xml_has_atrribute(edge,'allow')):
                vtypes = edge['allow'].split(' ')
                for j,vt in enumerate(edge_allow):
                    if vt in vtypes:
                        edge_allow[j] = 1
                    continue
            
            # Lastly it has the dissalow tag, and what is not speficied is allowed
            elif (purr.xml_has_atrribute(edge,'disallow')):
                vtype_allowed = [1 for item in edge_allow]
                vtypes = edge['allow'].split(' ')
                for j, vt in enumerate(edge_allow):
                    if vt in vtypes:
                        edge_allow[j] = 0
                    continue
                    
            # ~ for j,vt in enumerate(edge_allow):
                # ~ print(edge_allow[j],vtype_allowed[j])
                
            for vt in vtype_allowed:
                csv.write(',%d' % (vt))
            csv.write('\n')
                
            n+=1; purr.update(n,total,'Writing edges.csv ')
            continue
        pass
        print('\nComplete.')
    return    

# Parses length from shape string
def shape_len(shape_str):
    xy_str = shape_str.split(' ')
    x = []; y = []
    for xy in xy_str:
        x_str, y_str = xy.split(',')
        x.append(float(x_str))
        y.append(float(y_str))
    length = 0
    for i in range(1,len(x)):
        length += dist(x[i-1],y[i-1],x[i],y[i])
    return length

# Distance between two points
def dist(x0,y0,x1,y1):
    return math.sqrt(math.pow(x0-x1,2) + math.pow(y0-y1,2))
    
if __name__ == "__main__":
    main()
