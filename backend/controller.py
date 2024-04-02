#this file contains the controller functions for the dependency parser
import re
import config
import requests
import networkx as nx
import matplotlib.pyplot as plt
import json



logger = config.logger



class DependencyController():
    ### Dependency Controller will contain functions that enable us to parse requirments and dependencies and turn them into a tree structure of hierarchical data
    
    
    
    def  __init__(self):
        logger.info("Initializing Dependency Controller")
        self.temp = 0
        self.graph = nx.DiGraph()
    
    @staticmethod
    def get_requirements(package , version):
        """
        This  function takes a package name and its version as input, and returns an array of dependencies that are required
        """
        try:
            logger.info('')
            requirements = {}
            url = 'https://pypi.python.org/pypi/' + str(package) + '/' + str(version) + '/json'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = json.loads(response.text)
                if not data['info']['requires_dist']:
                    return {"message" :{}, "status": "success"}
                for dependency in data['info']['requires_dist']:
                    if 'extra' not in dependency:
                        match = re.match(r"^(.+?)\s\(([^)]*)\)" ,dependency)
                        packageName = match.group(1)
                        specifier = match.group(2)
                        requirements[packageName] = {
                            "package_name": packageName,
                            "curr_version": None,
                            "list_versions": [],
                            "reqd_version":  specifier,
                            "flag": False 
                        }
                return {"message" :requirements, "status": "success"}
                
            else :
                raise Exception("Failed to fetch package information")
        except Exception as e:
            logger.info(str(e))
            return {"error" : "Error while getting dependencies"} 
        
    @staticmethod
    def get_available_versions(package):
        """
        This  method returns a list of available versions for the given package.
        It uses PyPI JSON API to retrieve this information. If there is any error during the process it logs that error and returns an empty list
        """
        try:
            logger.debug('Getting available versions for %s', package)
            url = 'https://pypi.python.org/pypi'+ str(package)+'/json'
            response = requests.get(url,timeout=5)
            # If request is successful, extract version numbers from JSON response and store it in a list
            if response.status_code==200:
                data = response.json()
                versions = []
                for release in data['releases'].keys:

                    if 'r' not in release:
                        versions.append(release)
                    versions.sort(reverse=True)
                    return {"versions":versions, 'status':'success'}
                return  {'versions':[],'status':'failure'}
        except Exception as e:
            logger.error(e)
            return {'versions':[],'status':'fail; network error'}  
        
    @staticmethod
    def upload_file(file):
        """
        This method is called when a user uploads a requirements txt file
        It will parse the uploaded file and call 'get_available_versions' to fetch all available versions of that package and add it to a python dictionary.
        """
        try:
            content = file.decode(encoding='utf-8')
            lines = file.read().splitlines()

            requirements = {}
            for line in lines:
                if line:
                    name = line.strip().split("==")[0]
                    version = line.strip().split(name+"==")[1].replace('"','').strip()
                    temp = DependencyController.get_available_versions(name)
                    requirements[name]={
                        "package_name":name,
                        "curr_version":version,
                        "list_versions":temp['versions'] if "versions" in temp else  [],
                        'reqd_versions':[],
                        'flag':False}
                    
            return {"message": requirements, "status": "success"}
        except:
            return {"message":"Error processing the uploaded file", "status": "failure"}
        
    @staticmethod
    def create_dag(packages):
        """
        This  function creates a directedacyclic graph (DAG) from the packages provided by the user.
        The DAG will be used to process the packages and display them in a graph/tree structure.
        """

        try:
            dag = nx.DiGraph()
            seen = set()
            for package in packages:
                p_name =  package["package_name"]
                p_version =  package["curr_version"]
                requirements = DependencyController.get_requirements(p_name, p_version).lower()
                nodes = [n.strip() for n in requirements.split(",")]
                for node in nodes:
                    # Avoid cycles
                    if node not in seen:
                        dag.add_edge(node)
                        seen.add(node)
                        dag.nodes[node[0]][node[1]]
                return  {"message": {"dag":dag }, "status": "success"}
            
        except Exception as e:
            logger.error(e)
            return {"message":"Error creating the Directed Acyclic Graph.", "status": "failure"}
        
    @staticmethod
    def parse_dependency_graph(self, pack_list):
        """
        This method is called when a list of  dependencies are received from npmjs or pipy. It parses the response into a directional acyclic graph.
        This method takes a list of dictionaries containing information about each package and its dependencies.

        """
        try:
            for package , content in pack_list['message'].items():
                if content['package_name'] not in self.graph:
                    self.graph.add_node(content['package_name'], **content )
                    for key,val in  content.items():
                        self.graph.nodes[package][key]  = val
            for package, content in pack_list['message'].items():
                req_response = DependencyController.get_requirements(content['package_name'], content['curr_version'])['message']
                for req , content in req_response.items():
                    if req not in self.graph.nodes:
                        self.graph.add_node(req)
                        temp = DependencyController.get_available_versions(req)['message']
                        #add a code snippet to pick version for the curr version form the req_version

                        for key,val in content.items():
                            self.graph.nodes[package][key]  = val

                        self.graph.nodes[req]['list_versions'] = temp['versions'] if 'versions' in temp else []

                    else:
                        self.graph.nodes[req]['reqd_version'] = content['reqd_version']
                    self.graph.add_edge(package, req)

                    #DependencyController.
            return {"message" : (nx.to_dict_of_lists(self.graph), dict(self.graph.nodes[req])), "status": 'success'} 
        except Exception as e:
            logger.error(e)
            return {"message":"Error in parse_dependency_graph", "status": "failure"}
        
    @staticmethod
    def check_recurse_requirements(self, package):
        """
        This method recursively goes through the graph and at every node recursively goes on to check its dependencies.

        """
        req_response = DependencyController.get_requirements(content['package_name'], content['curr_version'])['message']
        for req , content in req_response.items():
            if req not in self.graph.nodes:
                self.graph.add_node(req)
                temp = DependencyController.get_available_versions(req)['message']
                #add a code snippet to pick version for the curr version form the req_version

                for key,val in content.items():
                    self.graph.nodes[package][key]  = val

                self.graph.nodes[req]['list_versions'] = temp['versions'] if 'versions' in temp else []

            else:
                self.graph.nodes[req]['reqd_version'] = content['reqd_version']
            self.graph.add_edge(package, req)
        
        return {"message":{},"status" : "success"}
    
    @staticmethod
    def conflict_check(self, packages):
        
        graph = nx.from_dict_of_dicts(packages, create_using=nx.DiGraph())

        for node in graph.__iter__():
            req_condition = graph[node]['req_version']
            cur_version = graph[node]['cur_version']
            req_conds = list(req_condition.split(','))
            check = True
            for cond in req_conds:
                op = cond[:1]
                ver = cond[1:]
                if not eval(cur_version+op+ver):
                    check = False
            if not check:
                self.graph[node]['flag'] = True
                #return {'message':'Conflict detected! {} is required by {}, but its current version is {}.'.format(req_condition,node,cur_version)}

        return  {'message':{'conflict':False},'status':'success'}
    
    @staticmethod
    def process_packages(user_params, packages):
        """
        
        """
        try:
            filtered_packages = {}
            for name , package in packages.items():
                if user_params["python_version"] and package["condition"]:
                    condition = package["condition"].strip()
                    if  condition.startswith("python"):
                        condition_version = condition.split("=")[1]
                        if condition_version != user_params["python_version"]:
                            continue
                    elif condition.startswith('extra'):
                        continue
                filtered_packages[name]=package
            return {"message":filtered_packages,"status":"success"}
        except Exception as e:
            logger.error(e)
            return {"message":"", "status":"failure"}
