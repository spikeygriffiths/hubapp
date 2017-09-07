<?php 
error_reporting(E_ALL); 

echo "<html><head>";
echo "</head><body>";
echo "<center><h1>Recent error logs</h1></center>";
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
    # Could have an option to clear out errors
} else {
    echo "<center><h3>No error logs</h3></center>";
}
echo "<center>";
echo "<button type=\"button\" onclick=\"window.location.href='/vesta/index.php'\">Home</button><br><br>";
echo "</body></html>";
?>
