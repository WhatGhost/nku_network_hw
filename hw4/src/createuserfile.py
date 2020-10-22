import pickle

tmp = {}
with open(r"Logeduser.txt", "wb") as f:
        pickle.dump(tmp,f)
