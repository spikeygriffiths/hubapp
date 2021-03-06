<?php
include "database.php";
include "functions.php";
include "header.php";   # Has other includes as well as log-out detection, and favicon.  NB Has "<html><head>" for favicon link!
echo "<style>table {font-family:arial, sans-serif;border-collapse: collapse;width: 100 % }";
echo "td, th {border: 2px solid #dddddd;text-align: left;padding: 2px }";
echo "tr:nth-child(even) { background-color: #dddddd; }</style>";
echo "</style></head>";
echo "<body>";
$table = $_GET['table'];
PageHeader("Database Table Stats for ".$table);
$db = DatabaseInit();
ShowTableStats($db, $table);
echo "<br>";
echo "<button class=\"button\" type=\"button\" onclick=\"window.location.href='/vesta/DatabaseStats.php'\">Database Stats</button><br><br>";
PageFooter();
echo "</body></html>";

function ShowTableStats($db, $table)
{
    $numDevs = GetDevCount($db);
    if ($numDevs > 0) {
        $dbTableInfo = array();
        for ($index = 0; $index < $numDevs; $index++) {
            $devKey = GetDevKey($index, $db);
            $entries = GetCount($db, $table, "devKey=".$devKey);
            $dbTableInfo[] = array($devKey, $entries);
        }
        usort($dbTableInfo, "BySize");  # Sort by size (element 1 of each array)
        echo "<table>";
        echo "<tr><th>Device</th><th>Last 24 hours</th><th>Last 7 days</th><th>Total</th></tr>";
        foreach ($dbTableInfo as $info) {
            $devKey = $info[0];
            $username = GetDevItem("userName", $devKey, $db);
            $entries = $info[1];
            if ($entries > 100) {
                echo "<tr>";
                echo "<td><a href=\"/vesta/ShowOneDevice.php/?devKey=",$devKey,"\">",$username,"</a></td>";
                ShowStat($db, $table, "devKey=".$devKey." and timestamp>datetime('now', '-24 hours')");
                ShowStat($db, $table, "devKey=".$devKey." and timestamp>datetime('now', '-7 days')");
                echo "<td>",$entries,"</td>";
                echo "</tr>";
            }
        }
        echo "<tr>";
        echo "<td><b>Totals</b></td>";
        ShowStat($db, $table, "timestamp>datetime('now', '-24 hours')");
        ShowStat($db, $table, "timestamp>datetime('now', '-7 days')");
        ShowStat($db, $table);
        echo "</tr>";
        echo "</table>";
    }
}

function BySize($a, $b) {   # Sort by size (element 1 of each array)
    return ($a[1] < $b[1]);
}

function ShowStat($db, $table, $cond)
{
    $entries = GetCount($db, $table, $cond);
    echo "<td>",$entries,"</td>";
}

?>
