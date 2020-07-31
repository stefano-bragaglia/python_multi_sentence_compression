autostash NEO4J_CONF=$(pwd)
autostash NEO4J_PASS='password'
if [[ $autoenv_event == 'enter' ]]; then
#    echo dbms.directories.data=$(pwd)/neo4j/data > $(pwd)/neo4j.conf
#    echo dbms.directories.plugins=$(pwd)/neo4j/plugins >> $(pwd)/neo4j.conf
#    echo dbms.directories.import=$(pwd)/src/main/data/processed >> $(pwd)/neo4j.conf
#    echo 'dbms.security.procedures.unrestricted=apoc.*' >> $(pwd)/neo4j.conf
    if [[ -a .env/bin/activate ]]; then
        source .env/bin/activate
    elif [[ -a .venv/bin/activate ]]; then
        source .venv/bin/activate
    fi
elif [[ $autoenv_event == 'leave' ]]; then
    if type deactivate > /dev/null; then
        deactivate
    fi
else
    autoenv_source_parent ../..
fi
