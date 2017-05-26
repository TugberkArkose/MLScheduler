for i in Paper2_*
do 
    cd $i
    rm -r *_base*
    rm -r *_ml*
    cd run
    ls | grep all_*
    chmod +x all_*.sh
    qsub -l big all_*.sh
    cd ../../
done
