
<html>
<head>
<title>Chronos</title>
<style>
.header {
    -webkit-writing-mode:vertical-rl; 
    -ms-writing-mode:tb-rl; 
    writing-mode:vertical-rl;
}

.node{
    font-weight:bold;
    font-size:150%;
}

.mixed{
    color:#ff7f0e;
}

.crash{
    color:#FF1493;
}

.better3{
    color:#32CD32;
    font-size:200%;
}
.better2{
    color:#64CD64;
    font-size:175%;
}
.better{
    color:#98CD98;
}

.nochange{
    color:#4169E1;
}

.worse{
    color:#B99999;
}
.worse2{
    color:#B66666;
    font-size:175%;
}
.worse3{
    color:#B22222;
    font-size:200%;
}



.bar {
  fill: steelblue;
}

.bar:hover {
  fill: brown;
}

.axis {
  font: 10px sans-serif;
}

.axis path,
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.x.axis path {
  display: none;
}
</style>
</head>
<body>
<?php
if (!isset($_GET['comparison'])) {
?>
<table style="width:100%">
    <tr>
        <td><button class="header" type="submit" form="comparison_form" value="Compare">Compare</button></td>
        <td>Database</td>
<?php
if (isset($_GET['branch'])) {
?>
        <td>Date</td>
<?php
} else {
?>
        <td>Branch</td>
<?php
}
?>
        <td>Revision</td>
        <td><span class="header">Q1</span></td>
        <td><span class="header">Q2</span></td>
        <td><span class="header">Q3</span></td>
        <td><span class="header">Q4</span></td>
        <td><span class="header">Q5</span></td>
        <td><span class="header">Q6</span></td>
        <td><span class="header">Q7</span></td>
        <td><span class="header">Q8</span></td>
        <td><span class="header">Q9</span></td>
        <td><span class="header">Q10</span></td>
        <td><span class="header">Q11</span></td>
        <td><span class="header">Q12</span></td>
        <td><span class="header">Q13</span></td>
        <td><span class="header">Q14</span></td>
        <td><span class="header">Q15</span></td>
        <td><span class="header">Q16</span></td>
        <td><span class="header">Q17</span></td>
        <td><span class="header">Q18</span></td>
        <td><span class="header">Q19</span></td>
        <td><span class="header">Q20</span></td>
        <td><span class="header">Q21</span></td>
        <td><span class="header">Q22</span></td>
    </tr>
    <form action="index.php" method="get" id="comparison_form">
<?php
if (isset($_GET['branch'])) {
    $branch = $_GET['branch'];
    $fp = fopen("htmloutput-$branch", "r") or die("Unrecognized branch!");
    echo fread($fp, filesize("htmloutput-$branch"));
    fclose($fp);
} else {
    $fp = fopen("htmloutput", "r") or die("Unable to open file!");
    echo fread($fp, filesize("htmloutput"));
    fclose($fp);
}
?>
    </form>
</table>
<?php
} else {
?>
<script src="//d3js.org/d3.v3.min.js"></script>
<script src="https://code.jquery.com/jquery-3.0.0.min.js"></script>
<script src="comparison.js"></script>
<?php
}
?>
</body>
</html>