exp_dir='/bp1store/mrcieu1/users/fu19841/kge/local/experiments'
for job in "$@"
do
    found_exp=false
    echo "Processing $job"
    name=${job%.sh}
    for loc in $exp_dir/*
    do
        if [[ "$loc" == *"$name" ]]
        then
            found_exp=true
            old_line=$(tail -n 1 $job) 
            new_line="kge resume $loc"
            sed -i "s@${old_line}@${new_line}@" $job
        fi
    done
    if ! $found_exp
    then
        echo "Couldn't find experiment folder for $job"
    fi
done