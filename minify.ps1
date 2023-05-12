New-Item "minified" -ItemType "Directory"

foreach ($file in Get-ChildItem)
{
	if ($file.Name.EndsWith(".py"))
	{
		$newname = "minified/"+$file.Name
		python -m python_minifier $file.Name --output $newname
	}
}