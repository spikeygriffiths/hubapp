<?php
include "database.php";
include "functions.php";
include "header.php";   # Has other includes as well as log-out detection, and favicon.  NB Has "<html><head>" for favicon link!
echo "</head><body>";
PageHeader("Configuration");
$db = DatabaseInit();
ShowConfig($db);
PageFooter();
echo "</body></html>";

function ShowConfig($db)
{
    $sth = $db->prepare("SELECT item FROM Config"); # Get all items
    $sth->execute();
    $itemCount = 0;
    while ($row =  $sth->fetch()) {
        $items[$itemCount++] = $row['item']; # Build array ready for sorting
    }
    sort($items, SORT_NATURAL | SORT_FLAG_CASE);  # Sort items
    echo "<table>";
    for ($index = 0; $index < $itemCount; $index++) {
        $item = $items[$index];
        $value = GetConfig($item, "", $db);
        echo "<tr><td>",$item,"</td><td>";
        echo "<form action=\"/vesta/save_config.php/?item=", $item, "\" method=\"post\">";
        echo "<input type=\"text\" size=\"50\" name=\"valueTxt\" value=\"", $value, "\">";
        echo "<input type=\"submit\" value=\"Update\"></form>";
        echo "</td></tr>";
    }
    echo "<tr><td>New Item</td><td>";
    echo "<form action=\"/vesta/save_config.php/?item=NewItem\" method=\"post\">";
    echo "<input type=\"text\" size=\"20\" name=\"valueTxt\" value=\"\"\>";
    echo "<input type=\"submit\" value=\"Update\"></form>";
    echo "</td></tr>";
    echo "</table>";
}
?>
