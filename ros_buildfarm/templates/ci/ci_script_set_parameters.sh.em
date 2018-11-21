# set default parameter values
@[for key, val in parameters.items()]@
@key="@val.replace('"', '\\"')"
@[end for]@
