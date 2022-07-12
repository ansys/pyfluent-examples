#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ansys.fluent.core as pyfluent

# In[2]:


pyfluent.set_log_level("DEBUG")


# In[3]:


session = pyfluent.launch_fluent(show_gui=True)


# In[4]:


session.check_health()


# In[5]:


session.solver.tui.file.read_case(case_file_name="elbow.cas.gz")


# In[6]:


session.solver.tui.solve.initialize.initialize_flow()


# In[7]:


session.solver.tui.solve.iterate(10)


# In[8]:


session.solver.tui.display.contour = {
    "boundary_values": True,
    "color_map": {
        "color": "field-velocity",
        "font_automatic": True,
        "font_name": "Helvetica",
        "font_size": 0.032,
        "format": "%0.2e",
        "length": 0.54,
        "log_scale": False,
        "position": 1,
        "show_all": True,
        "size": 100,
        "user_skip": 9,
        "visible": True,
        "width": 6.0,
    },
    "coloring": {"smooth": False},
    "contour_lines": False,
    "display_state_name": "None",
    "draw_mesh": False,
    "field": "pressure",
    "filled": True,
    "mesh_object": "",
    "node_values": True,
    "range_option": {"auto_range_on": {"global_range": True}},
    "surfaces_list": [2, 4],
}


# In[9]:


session.solver.tui.display.objects.display("contour-1")


# In[10]:


session.solver.tui.display.save_picture("contour.png")


# In[11]:


session.solver.root.setup.obj_name


# In[12]:


session.solver.tui.define.models.energy = False


# In[13]:


print(session.solver.tui.define.models.energy)


# In[14]:


# session.solver.tui.define.parameters.enable_in_TUI("yes")


# In[15]:


root = session.solver.root


# In[16]:


inlet = root.setup.boundary_conditions.velocity_inlet["inlet1"]


# In[17]:


inlet.vmag.constant = 1.2


# In[18]:


session.solver.root.solution.initialization()


# In[20]:


session.exit()


# In[ ]:
