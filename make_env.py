# -*- coding: utf-8 -*-
import re


def resolve_variables(value, variables):
    while True:
        new_value = value
        for var, val in variables.items():
            new_value = new_value.replace(f"${{{var}}}", val)
        if new_value == value:
            break  # Stop if no change
        value = new_value
    return value


def load_and_process_env(input_files: list, docker_file: str, output_files: list):
    variables = {}
    docker_variables = set()
    output_lines = {file: [] for file in output_files}

    # Read docker file to get list of variables to keep
    with open(docker_file, "r") as f:
        for line in f:
            match = re.match(r'export (\w+)="(.*)"', line.strip())
            if match:
                key, _ = match.groups()
                docker_variables.add(key)

    # Read and process each input file
    for input_file in input_files:
        with open(input_file, "r") as f:
            for line in f:
                match = re.match(r'export (\w+)="(.*)"', line.strip())
                if match:
                    key, value = match.groups()
                    variables[key] = resolve_variables(value, variables)

    # Write values to output files
    for output_file in output_files:
        for key, value in variables.items():
            resolved_value = resolve_variables(value, variables)

            # Only replace variables in .docker with 127.0.0.1 when writing to .env
            if output_file == ".env":
                for docker_var in docker_variables:
                    resolved_value = re.sub(
                        rf"(?<=[:/@]){re.escape(variables.get(docker_var,
                                                              docker_var))}(?=[:/@])",
                        "127.0.0.1",
                        resolved_value,
                    )
                    if key in docker_variables:
                        resolved_value = "127.0.0.1"

            output_lines[output_file].append(f'export {key}="{resolved_value}"')

    # Write to output files
    for output_file, lines in output_lines.items():
        with open(output_file, "w") as f:
            f.write("\n".join(lines) + "\n")


# Usage
load_and_process_env([".env.example"], "environments/.docker", [".docker.env", ".env"])
