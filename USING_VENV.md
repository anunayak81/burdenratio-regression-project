# Using a Python Virtual Environment (venv)

A virtual environment (venv) helps you manage dependencies for your project in isolation from other Python projects and system packages. Here’s how to create and use a venv for your project:

## 1. Create a Virtual Environment

Open a terminal in your project directory and run:

```
python -m venv .venv
```

This creates a folder named `.venv` containing your isolated Python environment.

## 2. Activate the Virtual Environment

- **On Windows:**
  ```
  .venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```
  source .venv/bin/activate
  ```

After activation, your terminal prompt will show `(.venv)`.

## 3. Install Project Dependencies

With the venv activated, install dependencies using pip:

```
pip install -r requirements.txt
```

Or, if using conda and `environment.yml`:

```
conda env create -f environment.yml
conda activate burdenratio-regression-project
```

## 4. Deactivate the Virtual Environment

When finished, deactivate with:

```
deactivate
```

## 5. Using venv in Jupyter Notebooks

If you use Jupyter, install the kernel:

```
pip install ipykernel
python -m ipykernel install --user --name=burdenratio-venv
```

Then select the `burdenratio-venv` kernel in your notebook interface.

---

**Tip:** Always activate your venv before running scripts or notebooks to ensure you’re using the correct dependencies.
