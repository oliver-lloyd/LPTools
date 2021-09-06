conf_dir='/bp1store/mrcieu1/users/fu19841/configs/'

for loc in "$@"
do 
    echo "Processing $loc"
    yaml="${loc/.sh/.yaml}" 
    old=$(tail -n 1 $loc) 
    new="kge start $conf_dir/$yaml";
    sed -i "s@$old@$new@" $loc
done