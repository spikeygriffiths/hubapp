<?php
error_reporting(E_ALL); 
include "HubCmd.php";

ini_set('display_errors', '1');
$devId=$_GET['devId'];   // Get deviceId to delete from URL
$cmd= "removeDevice ".$devId;
HubCmd($cmd, false);
echo "<html><head></head><body>";
echo "<script type='text/javascript'>alert('Device Removed')</script>"; // Show dialog box saying "Device Removed"
header('location:ShowAllDevices.php');   // and then go to showing All Devices, rather than back where we came from (since that's just been trashed)
echo "</body></html>";
?>