# 1. 3DFront to USD

    1. Follow the instruction in Load3DFront2Maya.ipynb

# 2. Blender notebook set up (Windows only)

## 0. Correct `pyzmq` in Anaconda

```
pip install --upgrade pyzmq
```

I uninstalled Anaconda and installed [miniconda](https://docs.conda.io/en/latest/miniconda.html) instead, then install `jupyter notebook`

```
conda install -c conda-forge jupyterlab
```


## 1. Download [Nvidia omniverse](https://www.nvidia.com/en-us/omniverse/) and install

## 2. Install `Blender 3.1 Alpha usd branch` from **omniverse exchange**

![omniverse_blender](imgs/omniverse_blender.png)

## 3. Open **Blender 3.1 Alpha usd branch** from omniverse, save the system info from `blender 3.1 alpha`

![blender_info](imgs/blender_info.png)

## 4. Get the **saved text** file and get the `blender exe path` (we will use it for the `blender notebook`)

![blender_path](imgs/blender_path.png)

## 5. Install [Blender jupyter notebook](https://pypi.org/project/blender-notebook/); follow the instructions and replace your **blender_path** as the path we found the the **system_info.txt**

![notebook_setup](imgs/notebook_setup.png)

## 6. Start blender from jupyter notebook


import sys 
omniverse_plugin_path = 'C:/Users/Yizhou Zhao/AppData/Local/ov/pkg/maya-connector-102.4.0/20200/scripts'
sys.path.append(omniverse_plugin_path)
from testcases import *


folder = OmniTC_BaseFolder + '/auto_tester_maya3'
OmniTC_MakeFolderExistAndClean(folder)
OmniTC_MakeSureConnected()
fn = folder + '/test0.usd'

# export options
mel.eval('optionVar -iv "omniverse_export_split_files" 0')
mel.eval('optionVar -iv "omniverse_export_includemdl" 1')
mel.eval('optionVar -iv "omniverse_export_mdl_copy_option" 1')   #default
mel.eval('optionVar -iv "omniverse_embed_materials" 1')
mel.eval('optionVar -iv "omniverse_export_includeUSDPreviewSurface" 0')
mel.eval('optionVar -iv "omniverse_export_stripnamespace" 0')

cmds.OmniExportCmd(f=fn)

