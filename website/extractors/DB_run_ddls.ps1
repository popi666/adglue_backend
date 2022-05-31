#Install-Module SqlServer -Scope CurrentUser #funguje
#Invoke-Sqlcmd -ServerInstance "baseadpoint.database.windows.net" -Database "vdfsdfv" -InputFile "DDL\Tables\DDL__schemas.sql" -Username "adpoint" -Password "RDmCVIKuUPFhnBR9PwJ3" -Verbose

function load_DDLs($database, $script) {

    Invoke-Sqlcmd -ServerInstance "baseadpoint.database.windows.net" -Database $database -InputFile $script -Username "adpoint" -Password "RDmCVIKuUPFhnBR9PwJ3" -Verbose

}
