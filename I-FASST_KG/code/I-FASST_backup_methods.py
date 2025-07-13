def find_all_interaction_paths(self, queries):
        # paths_array = self.find_all_paths_in_graph(queries, SEARCH_DEPTH)
        # paths_array = self.find_all_interaction_paths_in_one_query(queries, SEARCH_DEPTH)

        for query in queries:
            lifeline1 = query[0]
            lifeline2 = query[1]
            if lifeline1 == lifeline2:
                continue # skip messages from a lifeline to itself
            
            paths_array = self.search_for_paths_with_intermediate_nodes(lifeline1, lifeline2, SEARCH_DEPTH)
            if len(paths_array) > 0:
                for path in paths_array:
                    all_nodes = path['all_nodes']
                    self.all_interaction_paths.append((path, lifeline1, lifeline2))


def search_for_paths_with_intermediate_nodes(self, lifeline1, lifeline2, max_length = 10):
    query = f"""
        MATCH p = (n) -[*..{max_length}]-> (m)
        WHERE n.node_id = $start_value AND m.node_id = $end_value 
        AND ALL(r IN relationships(p) WHERE r.diagram_id = head(relationships(p)).diagram_id)
        WITH p, nodes(p) AS all_nodes
        RETURN p, all_nodes
        LIMIT 1
    """
    
    start_value = lifeline1.get('node_id')
    end_value = lifeline2.get('node_id')
    result = self.graph.run(query, start_value=start_value, end_value=end_value)
    data = result.data()
    return data


def create_projection(self):
        query = """
        MATCH (src:`uml:Lifeline`)
        OPTIONAL MATCH (src)-[r:MESSAGE]->(trg:`uml:Lifeline`)
        RETURN gds.graph.project(
        'cypherGraph19',
        src,
        trg,
        {
            relationshipType: type(r),
            relationshipProperties: r { .package }
        },
        { directedRelationshipTypes: ['MESSAGE'] }
        )
        """
        result = self.graph.run(query)
        data = result.data()
        return data
    
def find_dijkstra_path(self, lifeline1, max_length = 10):
    # Finds paths between the source node and a list of destination nodes 
    query = ""
    query_safety = """
    MATCH (source:`uml:Lifeline` { node_id: $source_id }), (target:`uml:Lifeline` { safety_relevance: True})
    CALL gds.shortestPath.dijkstra.stream('cypherGraph19', {
        sourceNode: source,
        targetNodes: target
    })
    YIELD sourceNode, targetNode, path
    RETURN
        gds.util.asNode(sourceNode).name AS sourceNodeName,
        gds.util.asNode(targetNode).name AS targetNodeName,
        path AS p, nodes(path) AS all_nodes
    """
    
    query_security = """
    MATCH (source:`uml:Lifeline` { node_id: $source_id }), (target:`uml:Lifeline` { safety_relevance: True})
    CALL gds.shortestPath.dijkstra.stream('cypherGraph19', {
        sourceNode: source,
        targetNodes: target
    })
    YIELD sourceNode, targetNode, path, properties
    RETURN
        gds.util.asNode(sourceNode).name AS sourceNodeName,
        gds.util.asNode(targetNode).name AS targetNodeName,
        path AS p, nodes(path) AS all_nodes
    """

    relevance = 'None'
    if lifeline1 in self.se_lifelines:
        relevance = 'safety_relevance'
        query = query_safety
    elif lifeline1 in self.sa_lifelines:
        relevance = 'security_relevance'
        query = query_security

    result = self.graph.run(query, source_id=lifeline1.get('node_id'), relevance=relevance)
    data = result.data()
    return data
    
def find_bellman_ford_path(self, lifeline1):
    # Finds paths between the node and all reachable nodes (if use this, the whole time is about 44 seconds)
    query = """MATCH (source:`uml:Lifeline` { node_id: $source_id})
    CALL gds.bellmanFord.stream('cypherGraph17', {
    sourceNode: source
    })
    YIELD index, sourceNode, targetNode, route 
    RETURN
        gds.util.asNode(sourceNode).name AS sourceNode,
        gds.util.asNode(targetNode).name AS targetNode,
        route as p, nodes(route) as all_nodes
    """
    result = self.graph.run(query, source_id=lifeline1.get('node_id'))
    data = result.data()
    return data


def find_optimized_interaction_paths(self):
    # self.create_projection()
    queries = []
    for se_lifeline in self.se_lifelines:
        queries.append(se_lifeline)
    for sa_lifeline in self.sa_lifelines: 
        queries.append(sa_lifeline)
    for query in queries:
        paths_array = self.find_dijkstra_path(query)
        # paths_array = self.find_bellman_ford_path(query)
        for path in paths_array:
            all_nodes = path['all_nodes']
            lifeline1 = all_nodes[0]
            lifeline2 = all_nodes[len(all_nodes) - 1]
            if lifeline1 == lifeline2:
                continue
            if lifeline1 in self.sa_lifelines or lifeline1 in self.se_lifelines or lifeline1 in self.sa_se_lifelines:
                if lifeline2 in self.sa_lifelines or lifeline2 in self.se_lifelines or lifeline2 in self.sa_se_lifelines:
                    self.all_interaction_paths.append((path, lifeline1, lifeline2))