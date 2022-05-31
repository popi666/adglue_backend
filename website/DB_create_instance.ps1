#New-AzSqlDatabase -ResourceGroupName 'Adpoint' -ServerName 'baseadpoint' -DatabaseName 'Jano_testuje' -Edition 'Basic'
#Set-AzContext -Subscription "90227f4e-d86e-4cb4-93bf-cdd0611978ee"
#Connect-AzAccount

Function createDBinstance($name) {
    $User = "adpoint@base.cz"
    $PWord = ConvertTo-SecureString -String "Qepma6-jajxev-pejgak" -AsPlainText -Force
    $tenant = "32b05504-4594-4ff6-b8b4-2df23b2abadd"
    $subscription = "90227f4e-d86e-4cb4-93bf-cdd0611978ee"
    $Credential = New-Object -TypeName "System.Management.Automation.PSCredential" -ArgumentList $User, $PWord
    Connect-AzAccount -Credential $Credential -Tenant $tenant -Subscription $subscription
    # New-AzSqlDatabase -ResourceGroupName 'Adpoint' -ServerName 'baseadpoint' -DatabaseName $name -Edition 'Basic'
    New-AzSqlDatabaseCopy -ResourceGroupName "Adpoint" -ServerName 'baseadpoint' -DatabaseName 'Nutraceutics' -CopyResourceGroupName "Adpoint" -CopyServerName "baseadpoint" -CopyDatabaseName $name

}

