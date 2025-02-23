# Img2Particle.py

**Purpose:**  
Img2Particle is a simple, in-house Python script that converts a grayscale image into a particle model arranged in a hexagonal packing structure. The resulting particle model is saved in a LAMMPS data file format.

---

## Key Components

### 1. Imports and Dependencies
- **Standard Libraries:**  
  - `os`, `argparse`, `glob`, `math` for file handling, command-line argument parsing, and mathematical operations.
  - `numpy` for numerical operations.
- **Image Processing:**  
  - `PIL` (Python Imaging Library) is used to open and convert images.
- **Date and Time:**  
  - `datetime` is used to stamp the output file with the creation time.

---

### 2. Argument Parsing (`parse_args()`)
- **Command-Line Options:**  
  The script uses `argparse` to let users specify:
  - **Input image file** (`-infile`): The path to the image to be processed.
  - **Output file** (`-o`): The base name for the output LAMMPS data file.
  - **Model dimensions** (`-lx`, `-ly`, `-lz`): The physical size of the simulation box.
  - **Lattice constant** (`-s`): The particle spacing.
  - **Particle types** (`-t`): Number of different particle types.
  - **Notch dimensions** (`-n`): Dimensions for creating a notch (defect) in the model.
- **Version Information:**  
  Users can display the script version using the `--version` flag.

---

### 3. Image Import and Conversion (`import_img`)
- **Process:**  
  - Opens the specified image file.
  - Converts it to grayscale.
  - Converts the grayscale image to a NumPy array for later use in determining particle types.

---

### 4. Model and Lattice Setup
- **Model Parameters:**  
  - Reads model dimensions (`lx`, `ly`, `lz`) and the lattice constant (`s`) from the command-line arguments.
- **Hexagonal Lattice Definition:**  
  - A unit cell for hexagonal packing is created.
  - The number of lattice points (`nx`, `ny`, `nz`) is calculated based on the simulation box size and unit cell dimensions.
  - Margins are added to the lattice grid to ensure proper boundary conditions.

---

### 5. Atom Creation
- **Atom Array Initialization:**  
  An array is set up to hold atom properties (such as id, molecule, type, coordinates, etc.).
- **Hexagonal Packing:**  
  Two atoms are created per lattice site with a half-unit shift to form a hexagonal structure.
- **Looping Over Lattice Indices:**  
  Nested loops iterate over `nx`, `ny`, and `nz` to assign positions to each atom.

---

### 6. Assigning Particle Types Based on the Image
- **Histogram Analysis:**  
  The script computes a histogram of the pixel intensities from the image to determine thresholds for assigning different particle types.
- **Mapping Positions to Image Coordinates:**  
  For each atom, its (x, y) position is mapped to the corresponding pixel in the image.
- **Type Assignment:**  
  Atom types are set based on the pixel intensity relative to the histogram bins.

---

### 7. Creating a Notch (Defect)
- **Notch Filtering:**  
  A logical condition is applied to remove atoms within a specified notch region. This simulates a defect in the model.
- **Atom Re-indexing:**  
  After filtering, atom IDs are re-assigned sequentially.

---

### 8. Output File Generation
- **LAMMPS Data Format:**  
  The script writes a LAMMPS data file including:
  - A header with a timestamp.
  - Number of atoms and atom types.
  - Simulation box dimensions.
  - Masses for each particle type.
  - Atom information (formatted for the bond style, to be used with LAMMPS' `create_bonds` command).
- **File Naming:**  
  The output file name is determined by the user-provided argument.

---

## Example Usage

```bash
# simple sample
python Img2Particle.py -infile my_image.png -o my_model
# costum sample
python Img2Particle.py -infile my_image.png -o my_model -lx 0.00816 -ly 0.00816 -lz 1 -s 0.00003657 -t 2 -n 7.968e-5 1.083e-3
```

# input_real_LSM.in
This LAMMPS input script performs a **2D axial tensile test** simulation. It is designed to study the mechanical response of a material (e.g., a bone model) under stretching. Below is a breakdown of its main sections:

---

## 1. Settings and Parameter Initialization
- **Rootname**:  
  Sets the base name for input and output files.
- **Bond Length (lb)**:  
  Defines the initial bond length.
- **Strain Rate (erate) & Final Strain (efinal)**:  
  Controls how fast and how much the sample is stretched.
- **Minimization & Output Intervals**:  
  Variables like `fmin`, `nmin`, `nthm`, etc., determine how frequently energy minimization is performed and data is output.

---

## 2. LAMMPS Initialization
- **Units and Dimensions**:  
  Uses `real` units and sets the simulation to 2D.
- **Boundary Conditions**:  
  Periodic boundaries in the x and y directions; specific handling in the z direction.

---

## 3. Geometry and Group Setup
- **Reading the Data File**:  
  The script reads initial structure and bond information from a data file.
- **Region Definitions**:  
  Divides the simulation box into left (fixed) and right (fixed) regions.
- **Group Assignments**:  
  - **LEFT/RIGHT**: Atoms in the fixed boundary regions.  
  - **MOBILE**: Atoms in the interior that are free to move.

---

## 4. Bond Creation and Force Field Setup
- **Pair Style and Coefficients**:  
  Sets a simple bond interaction (harmonic potential) with a zero pair style.
- **Bond Types**:  
  Differentiates between stiff and soft bonds by creating them within a specific distance range.
- **Force Field Parameters**:  
  Defines the stiffness constants and bond breakage criteria for different bond types.

---

## 5. Simulation Execution
- **Fixed Boundary Conditions**:  
  Applies forces to the LEFT and RIGHT groups to keep them fixed in certain directions.
- **Time Integration**:  
  Uses the NVE integration scheme for the MOBILE group.
- **Tensile Test Loop**:  
  - The script sets up a loop with `variable i loop 200`, meaning **200 cycles**.
  - **Within Each Cycle**:
    - Energy minimization is performed.
    - A tensile load is applied by moving the fixed boundaries.
    - The simulation runs for **10,000 timesteps** per cycle.
- **Total Simulation Steps**:  
  \(200 \text{ cycles} \times 10,000 \text{ steps} = 2,000,000 \text{ steps}\)
- **Timestep Duration**:  
  Each timestep is 0.1 femtoseconds, giving a total simulation time of:  
  \(2,000,000 \times 0.1 \text{ fs} = 200,000 \text{ fs}\)  
  (which equals 0.2 nanoseconds).

---

## 6. Data Output
- **Stress-Strain Data**:  
  The script outputs stress, strain, and bond count information into a file for later analysis.
- **Intermediate Data Files**:  
  Periodic data dumps are made during the loop to capture intermediate states.

---
## Example Usage

```bash
# modify rootname before running
lmp -in input_real_LSM.in
```
