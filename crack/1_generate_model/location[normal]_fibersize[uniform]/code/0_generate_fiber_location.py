# %%
from ovito.data import *
from ovito.modifiers import *
from ovito.pipeline import *
from ovito.io import *
import numpy as np
import pandas as pd
from pathlib import Path
import time
import argparse



# 解析命令行參數
parser = argparse.ArgumentParser(description="Generate fiber locations")
parser.add_argument("--seed1", type=int, required=True, help="First random seed for generating fibers")
parser.add_argument("--seed2", type=int, required=True, help="Second random seed for generating fibers")
args = parser.parse_args()

seed1 = args.seed1
seed2 = args.seed2

## some define functions

def generate_radius(area_limit, max_fiber, min_fiber, seed):
    np.random.seed(seed)

    initial_radii = np.random.uniform(min_fiber, max_fiber, 2000)
    rounded_radii = np.round(initial_radii, 7)

    particle_area = np.pi * rounded_radii ** 2
    cumulative_area = np.cumsum(particle_area)


    index = np.where(cumulative_area >= area_limit)[0][0]
    

    final_radii = rounded_radii[:index]
    
    sorted_radii = np.sort(final_radii)[::-1]
    return sorted_radii

### according to particle_radius, generate random position for each particle and check each particle is not overlap
def generate_position(particle_radius, seed):
   # 1 minute from now
    time_limit = time.time() + 120
    np.random.seed(seed)
    numofparticles = len(particle_radius)
    while True:  # 外層迴圈，確保可以重新執行整個過程
        if time.time() > time_limit:
            break
        particle_position = np.zeros((numofparticles, 2))
        timeout = time.time() + 20
        for i in range(0, numofparticles):
            while True:
                # 生成隨機點
                particle_position[i] = np.random.uniform(
                    -0.05 + particle_radius[i]+0.0001,
                    0.05 - particle_radius[i]-0.0001,
                    2
                )
                # 計算距離
                distances = np.linalg.norm(particle_position[:i] - particle_position[i], axis=1)

                # 如果符合條件，退出內層 while
                if np.all(distances >= (particle_radius[:i] + particle_radius[i])):
                    break
        
                if time.time() > timeout:
                    break
            if time.time() > timeout:
                break

        if i == numofparticles - 1:
            return particle_position
# %%

particle_radius = generate_radius(0.006,0.1/40,0.1/60,seed1)

df = pd.DataFrame(particle_radius,index=range(1,len(particle_radius)+1))
## add the column name
df.columns = ['particle_radius']
## add id from 1 to len(particle_radius)

particle_position = generate_position(particle_radius, seed2)



# %%
df['id'] = df.index
df['x'] = particle_position[:, 0]
df['y'] = particle_position[:, 1]
df['z'] = 0
## change the order of columns as id,x,y,z,particle_radius
df = df[['id', 'x', 'y', 'z', 'particle_radius']]


# %%
## create DataCollection object and create particles
data = DataCollection()
particles = data.create_particles()
### prepare the data for particles properties
pos = df[['x', 'y', 'z']].values
atom_id = df['id'].values
radius = df['particle_radius'].values
data = DataCollection()
particles = data.create_particles()
## set the properties for particles
atom_id_prop = particles.create_property('Particle Identifier', data = atom_id)
pos_prop = particles.create_property('Position', data = pos)
type_prop = particles.create_property('Particle Type')
radius_prop = particles.create_property('Radius', data = radius)
type_prop.types.append(ParticleType(id=2, name='fiber'))
type_prop[:] = 2
### create cell for the particles
lx = 0.1; ly = 0.1; lz = 0.0 # box size
matrix_pbc = np.zeros((3, 4))
matrix_pbc[:,0] = (lx, 0, 0)
matrix_pbc[:,1] = (0, ly, 0)
matrix_pbc[:,2] = (0, 0, lz)
## set the origin of the cell to the center of the box
matrix_pbc[:,3] = np.dot((-0.5, -0.5, -0.5), matrix_pbc[:3, :3])
## set cell for the DataCollection object
cell = data.create_cell(matrix_pbc, [False, False, False])

# %%
## set the pipeline
pipeline = Pipeline(source = StaticSource(data = data))
pipeline.add_to_scene

# %%
## export the file the second argument is the file name and the third argument is the file format, columns is the spec argument in lammps/dump file format
export_file(
    pipeline,
    f"../data/random_pos[{seed1}][{seed2}].dump",
    "lammps/dump",
    columns = ['Particle Identifier','Particle Type', 'Position.X', 'Position.Y', 'Position.Z', 'Radius'],
)


