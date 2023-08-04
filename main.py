"""
code mostly from https://github.com/argoproj-labs/applicationset-hello-plugin
which is a template repo but has no license
revisions by @jessebot and assumed to be whatever Argo's default license is
"""
import json
from json import loads
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import environ
import logging as log

PLUGIN_TOKEN = environ.get("TOKEN")


class Plugin(BaseHTTPRequestHandler):

    def args(self):
        """
        this just gets the args requested
        """
        return loads(self.rfile.read(int(self.headers.get('Content-Length'))))

    def reply(self, reply):
        """
        return 200 HTTP code (success) if auth everything checks out
        """
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(reply).encode("UTF-8"))

    def forbidden(self):
        """
        return 403 HTTP (forbidden) code if authorization fails
        """
        self.send_response(403)
        self.end_headers()

    def unsupported(self):
        """
        return 404 HTTP code if we are asked for any other path than getparams
        """
        self.send_response(404)
        self.end_headers()

    def return_env_vars(self, env_var_names: list):
        """
        Takes a list of of environment variables to return. We only return env
        vars that start with: ARGOCD_ENV_VAR_PLUGIN_

        We ignore all other requests to be kinda secure.
        """

        # list of dictionaries to return like {"envvar": "envar_value"}
        return_list = []

        # iterate through requested environment variables
        for env_var_name in env_var_names:
            log.info("Argo CD Env Var Plugin Generator recieved request for "
                     f"env var: {env_var_name}")

            if not env_var_name.startswith("ARGOCD_ENV_VAR_PLUGIN_"):
                log.warn("Argo CD Env Var Plugin Generator only returns "
                         "requests for environment variables that start with "
                         "ARGOCD_ENV_VAR_PLUGIN_")
            else:
                # creates a dict with the requested env var name and value and
                # appends it to the name list we will return
                return_list.append({env_var_name: environ.get(env_var_name)})

        return return_list

    def do_POST(self):
        # if the token is invalid, throw a forbidden error
        if self.headers.get("Authorization") != "Bearer " + PLUGIN_TOKEN:
            self.forbidden()

        if self.path == '/api/v1/getparams.execute':
            args = self.args()
            log.info(f"Argo CD Env Var full args payload: {args}")

            return_params = self.return_env_vars(args)

            # reply with all variables requested
            env_var_dictionary = {"output": {"parameters": return_params}}
            self.reply(env_var_dictionary)
        else:
            self.unsupported()


if __name__ == '__main__':
    httpd = HTTPServer(('', 4355), Plugin)
    httpd.serve_forever()
