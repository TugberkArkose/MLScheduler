rm IpcError.txt
for i in combinations_sp*_ml/*.o*;do python avarageBigSmallIpcParser.py $i; done

