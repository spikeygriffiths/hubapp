<?php
error_reporting(E_ALL);
include "database.php";

ini_set('display_errors', '1');
$oldGroupName=$_GET['oldName'];
$newGroupName = $_POST["NewName"];  // Get new user name from form
$db = DatabaseInit();
if ($oldGroupName == "NewGroup") {
    echo "New name is:", $newGroupName, "to be created<br>";
    $query = "INSERT INTO Groups (userName, devKeyList) VALUES (\"".$newGroupName."\",\"\")";  # Insert new name and empty string for devices
} else {
    echo "New name is:", $newGroupName, " to replace old name of:",$oldGroupName, "<br>";
    $query = "UPDATE Groups SET userName=\"".$newGroupName."\" WHERE userName=\"".$oldGroupName."\"";
}
echo "About to send ",$query, " to DB<br>";
$count = $db->exec($query);
if ($count == 1) {
    UpdateRules($oldGroupName, $newGroupName, $db);    // Now go through the rules and make sure the old name is updated to the new
    echo "<meta http-equiv=\"refresh\" content=\"1;url=/vesta/UpdateGroup.php/?groupName=",$newGroupName,"\"/>";
    echo "New name saved";
} else {
    echo "Update failed, with count of:", $count, "<br>";
}
echo "<a href=/vesta/UpdateGroup.php/?groupName=",$newGroupName,">Show Group</a>";
?>
