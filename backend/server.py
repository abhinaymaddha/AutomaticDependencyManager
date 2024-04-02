import config
from controller import *
from typing import List, Text, Union, Optional
from sanic import Sanic , response
from sanic_cors import CORS
from sanic.worker.loader import AppLoader
from functools import partial
import asyncio
import argparse


logger = config.logger

def create_argument_parser():
    """
    Parse all the  command line arguments and return an ArgumentParser object.

    """

    parser =  argparse.ArgumentParser(description="Starts the backend service")
    parser.add_argument('--hostname', type=str, default = "0.0.0.0", help = 'Hostname to bind server to')
    parser.add_argument("--port", type=int, default = 8080, help = 'port of the service')
    parser.add_argument('--cors', nargs="*", type = str, help= 'enable CORS for the passed origin. use '*' to allow from any source')

    return  parser

class DependencyRouter:

    def  __init__(self):
        logger.info('Dependency Router')

    def create_app(self, cors_origin = '*'):

        try:
            application = Sanic('myDepApp')
            application.config.RESPONSE_TIMEOUT = 60*60
            configure_cors(application, origin=[cors_origin])
            
            @application.get('/api/v1/healthcheck')
            async def health_check(request : Request) -> HTTPResponse:
                return json({"status": "UP"}, status=200)

        
        except Exception as e:
            logger.error(f'Failed to initialize the application {e}')
            raise SystemExit(e)


