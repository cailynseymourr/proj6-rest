<html>
    <head>
        <title>CIS 322 REST-api demo: Laptop list</title>
    </head>

    <body>
        <h1>List of laptops</h1>
        <ul>
            <?php
            $json = file_get_contents('http://laptop-service/');
            $obj = json_decode($json);
	          $laptops = $obj->Laptops;
            foreach ($laptops as $l) {
                echo "<li>$l</li>";
            }
            ?>
        </ul>
        <h1>All open and close times</h1>
        <ul>
             <?php
            $json = file_get_contents('http://laptop-service/listAll/json');
            $rows = json_decode($json);
            foreach ($rows as $r) {
                echo "<li>open: $r->open, close: $r->close</li>";
            }
            ?>
        </ul>

        <h1>Open times only</h1>
        <ul>
            <?php
            $json = file_get_contents('http://laptop-service/listOpenOnly/json');
            $rows = json_decode($json);
            foreach ($rows as $r) {
                echo "<li>$r->open</li>";
            }
            ?>
        </ul>

        <h1>Close times only (top 3)</h1>
        <ul>
            <?php
            $json = file_get_contents('http://laptop-service/listCloseOnly/json?top=3');
            $rows = json_decode($json);
            foreach ($rows as $r) {
                echo "<li>$r->close</li>";
            }
            ?>
        </ul>
    </body>
</html>