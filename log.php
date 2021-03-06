<?php 
include "header.php";   # Has other includes as well as log-out detection, and favicon.  NB Has "<html><head>" for favicon link!
include "database.php";
include "functions.php";
echo "</head><body>";
PageHeader("Recent error logs");
echo "</center>";
# See https://stackoverflow.com/questions/2667065/sort-files-by-date-in-php for details of the following sort
$files = glob("/home/pi/Vesta/*_err.log");
if ($files) {
    echo "<P>NB Most recent error log first in the following list;<br>";
    usort($files, function($a, $b) {
        return filemtime($a) < filemtime($b);
    });
    foreach($files as $file) {
        $logHandle = fopen($file, "r");
        $logText = fread($logHandle, 100000);
        echo "<h3>".$file."</h3>";
        echo nl2br($logText);
        echo "<br><br>";
    }
    echo "<button class=\"button\" type=\"button\" onclick=\"window.location.href='/vesta/DelLogs.php'\">Remove All Error logs</button><br><br>";
} else {
    echo "<center><h3>No error logs</h3></center>";
}
PageFooter();
echo "</body></html>";
?>
