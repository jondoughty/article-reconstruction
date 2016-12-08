<html>
<body>

<?php 
ini_set('memory_limit', '1024M');
$searchquery = null;
$searchfilter = 'article';

$searchquery = $_GET["name"];
$searchfilter = $_GET["filter"];

$pyscript = '/home/budhwar/MD_Search/search.py ';
$python = '/usr/local/bin/python3 ';

unset($output);
$cmd=$python.' '.$pyscript.' "'.$searchquery.'" '.$searchfilter.' 2>&1';
exec($cmd,$output,$status);
#$output = shell_exec($cmd);
if(count($output) == 7){
    if($output[1] != 'None'){
        print("<b>Publication: </b>");
        print_r(htmlspecialchars($output[1], ENT_COMPAT,'ISO-8859-1', true));
        echo "<br>";
        print("<b>Headline: </b>");
        print_r(htmlspecialchars($output[0], ENT_COMPAT,'ISO-8859-1', true));
        echo "<br>";
        print("<b>Page Number: </b>");
        print_r(htmlspecialchars($output[4], ENT_COMPAT,'ISO-8859-1', true));
        echo "<br>";
        print("<b>Article Number: </b>");
        print_r(htmlspecialchars($output[3], ENT_COMPAT,'ISO-8859-1', true));
        echo "<br>";
        print("<b>Author: </b>");
        print_r(htmlspecialchars($output[5], ENT_COMPAT,'ISO-8859-1', true));
        echo "<br>";
        print("<b>Article Date: </b>");
        print_r(htmlspecialchars($output[6], ENT_COMPAT,'ISO-8859-1', true));
        echo "<br>";
        print("<b>Article: </b>");
        print_r(htmlspecialchars($output[2], ENT_COMPAT,'ISO-8859-1', true));
        echo "<br>";
    }
    else{
    print("No Article's found");
    }
}
else{
print("No Article's found");
}
