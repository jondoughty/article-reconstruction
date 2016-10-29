$LIBRE_OFFICE_HOME="C:\Program Files (x86)\LibreOffice 5"
$PROJECT_HOME="C:\Daniels_Stuff\Classes\Current\grad_ai\project\repo\article-reconstruction"


ls $PROJECT_HOME\tagged_data\*.xlsx | % {
    & "$LIBRE_OFFICE_HOME\program\soffice.exe" --headless --convert-to csv:"Text - txt - csv (StarCalc):44,34,76,3" --outdir $PROJECT_HOME\tagged_data  ($_.FullName)
}

