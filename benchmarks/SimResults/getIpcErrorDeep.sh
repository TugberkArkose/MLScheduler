rm IpcError.txt
for i in combinations_sp*_ml_deep*/*.o*;do python avarageBigSmallIpcParser.py $i; done

