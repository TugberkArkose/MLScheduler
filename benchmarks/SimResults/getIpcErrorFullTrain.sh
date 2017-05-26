rm IpcError.txt
for i in combinations_sp*_ml_full*/*.o*;do python avarageBigSmallIpcParser.py $i; done

