# %%
from ovito.data import *
from ovito.modifiers import *
from ovito.pipeline import *
from ovito.io import *
import argparse


# %%
# 解析命令行參數
parser = argparse.ArgumentParser(description="Generate fiber locations")
parser.add_argument("--seed2", type=int, required=True, help="First random seed for generating fibers")
parser.add_argument("--seed3", type=int, required=True, help="Second random seed for generating fibers")
args = parser.parse_args()

seed1 = args.seed2
seed2 = args.seed3

filename = '../data/1_matrix.data'
pipeline = import_file(filename)
combinefilename = f'../data/random_pos[{seed1}][{seed2}].dump'
data = pipeline.compute()
modifier = CombineDatasetsModifier()
modifier.source.load(combinefilename)
pipeline.modifiers.append(modifier)
export_file(
    pipeline,
    'untrim.dump',
    "lammps/dump",
    columns = ['Position.X', 'Position.Y', 'Position.Z','Particle Type', 'Particle Identifier', 'Radius']
    )



# %%
pipeline = import_file("untrim.dump")
data = pipeline.compute()
### initialize the selection property as 0 for all particles
selection = data.particles_.create_property('Selection', data = 0)

## initial neighbor finder
cutoff = max(data.particles["Radius"])
neighbor_finder = CutoffNeighborFinder(cutoff, data)

## check numoffiber
ptype_prop = data.particles["Particle Type"]
numOfFiber = len(ptype_prop[ptype_prop == 2])
print(f"Number of fiber is {numOfFiber}")

### Interate over fiber
for index in (data.particles["Particle Identifier"][-numOfFiber:]-1):
    ## set cut off 
    cutoff = data.particles["Radius"][index] - 0.0001
    finder = CutoffNeighborFinder(cutoff,data)
    for neigh in finder.find(index):
        if selection[neigh.index] == 0:
            selection[neigh.index] = 1
### select particle according to selection == 1

def select_overlap_atoms(frame, data):
    data.particles_.create_property('Selection', data=selection)
pipeline.modifiers.append(select_overlap_atoms)
pipeline.modifiers.append(DeleteSelectedModifier())
pipeline.modifiers.append(SelectTypeModifier(property="Particle Type", types={2}))
pipeline.modifiers.append(DeleteSelectedModifier())
data = pipeline.compute()



export_file(
    pipeline,
    "3_trim.data",
    "lammps/data"
)



 




