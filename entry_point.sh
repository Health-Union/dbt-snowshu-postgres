#!/bin/bash

test(){
    echo "Running pytest"
    pytest
    pytest_exit_code=$?
    echo "Running prospector"
    bad_lines=$(prospector -M)
    pros_exit_code=$?
    if [[ $pros_exit_code == 0 ]]; then
        printf "\n\x1b[32mprospector passes!\x1b[0m\n"
    else
        printf "\n\x1b[31mprospector detected issues:\x1b[0m\n"
        printf "$bad_lines"
    fi
}
export -f test

$@
