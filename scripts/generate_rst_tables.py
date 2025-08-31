import inspect
import os
from meteofetch import arome, arpege, mfwam, aifs, ifs

models = [arome, arpege, mfwam, aifs, ifs]

output_dir = "docs/source/_static"
os.makedirs(output_dir, exist_ok=True)

for model in models:
    model_name = model.__name__.split('.')[-1]
    file_path = os.path.join(output_dir, f"{model_name}.rst")
    with open(file_path, "w") as f:
        f.write(f".. _{model_name}_variables:\n\n")
        for name, variable in model.variables.items():
            f.write(f'**{name}**\n')
            f.write('\n')
            f.write(f'   - {variable.description}\n')
            f.write('\n')
            if variable.levels is not None:
                f.write(f'   - levels: {variable.levels}\n')
                f.write('\n')
            f.write(f'   - grib params: ``{variable.grib_ids}``\n')
            f.write('\n')
            f.write(f'   - {variable.remote_server.name}\n')
            f.write('\n')
            if variable.remote_server.name == 'MeteoFrance':
                f.write(f'     - login required: {"**yes**" if variable.remote_server.login_required else "no"}\n')
                f.write('\n')
            f.write(f'     - available steps: ``{variable.remote_server.available_steps}``\n')
            f.write('\n')
