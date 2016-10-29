
# Add these to your environment variables or create a script defining them in one
# of the places defined here:
# https://technet.microsoft.com/en-us/library/bb613488(v=vs.85).aspx
#
#$LIBRE_OFFICE_HOME="C:\Program Files (x86)\LibreOffice 5"
#$CPART_HOME="C:\Daniels_Stuff\Classes\Current\grad_ai\project\repo\article-reconstruction"

if ("$CPART_HOME" -eq "") { echo '$CPART_HOME is not defined.'; exit 1; }
if ("$LIBRE_OFFICE_HOME" -eq "") { echo '$LIBRE_OFFICE_HOME is not defined.'; exit 1; }

ls $CPART_HOME\tagged_data\*.xlsx | % {
    & "$LIBRE_OFFICE_HOME\program\soffice.exe" --headless --convert-to csv:"Text - txt - csv (StarCalc):44,34,76,3" --outdir $CPART_HOME\tagged_data  ($_.FullName)
}

