# Import of the names of the client databases and template path
$currentDir = 'C:/Users/Josef Alb/Desktop/adpoint/Pshell'
$ExcelFile = $currentDir +'/metadata.xlsx'
$Excel = Import-Excel $ExcelFile | ? IsNew -eq 1
$ClientDatabases = @($Excel.ClientDatabase)
$TemplatePath = 'C:\Users\Josef Alb\Desktop\adpoint\Datovy reporting\2 Reporty\ReportTemplate\DataReportTemplateTest.pbix' 
$TargetWorkspace = 'AdPointTest' 

# Estabilish connection
Connect-PowerBIServiceAccount 

# Initializing new variables
$Datasets = @()
$WorkSpaceID = Get-PowerBIWorkspace -Name $TargetWorkspace | ForEach {$_.Id}
$InvokeInput = @()
$Row = @()

Foreach ($ClientDatabase in $ClientDatabases)
{
    # Updating the reports for the new clients
    New-PowerBIReport -Path $TemplatePath -Name $ClientDatabase -Workspace ( Get-PowerBIWorkspace -Name $TargetWorkspace )

    # Gather the data about their datasets
    $Datasets = Get-PowerBIDataset -WorkspaceId $WorkSpaceID  | Select Id, Name | Where {$_.Name -eq $ClientDatabase};

    # Prepare the input for the invoke function
    Foreach ($ID in $Datasets)
        {
        $Row = "" | Select Name, ParamUpdate, ParamRefresh, BodyUpdate, BodyRefresh
        $Row.Name = $ClientDatabase
        # Url for update parameter
        $Row.ParamUpdate = "/datasets/" + $Datasets.ID + "/Default.UpdateParameters"

        # Url for dataset refresh
        $Row.ParamRefresh = "/datasets/" + $Datasets.ID + "/refreshes"

        # Body for the parameter update
        $Row.BodyUpdate = '{

              "updateDetails": [

                {

                  "name": "ClientDatabase",

                  "newValue" : ' + ' "' + $Datasets.Name + '"' +

                 '
                 }

              ]

            }'

        # Body for the dataset refresh
        $Row.BodyRefresh = '(' + $Datasets.ID + ')'
        $InvokeInput += $Row
        }
}

# Changing parameter for the database in the PowerBI service
foreach ($Row in $InvokeInput){
    Invoke-PowerBIRestMethod -Url $Row.ParamUpdate  -Method Post -Body $Row.BodyUpdate -ContentType 'application/json';
    Write-Host "Changing database for client:" $Row.Name
    }

# Refresh new datasets in order to promote changes
foreach ($Row in $InvokeInput){
    Invoke-PowerBIRestMethod -Url $Row.ParamRefresh  -Method Post -Body $Row.BodyRefresh -ContentType 'application/json';
    Write-Host "Refreshing dataset for client:" $Row.Name
    }