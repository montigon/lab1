<!DOCTYPE html>
<html>
<head>
    <title>My lab</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>
    <body>
        <table align="center">
            <tr id="head">
                <th>Title</th>
                <th>Author</th>
                <th>#likes</th>
                <th>#comments</th>
                <th colspan="3">Label</th>
            </tr>
            %for row, color in rows:
                <tr class="row" id="{{color}}"" height="30px">
                    <td class="my" href="{{row.url}}"><a href="{{row.url}}">{{row.title}}</a></td>
                    <td>{{row.author}}</td>
                    <td>{{row.points}}</td>
                    <td>{{row.comments}}</td>
                    <td><a href="/add_label?label=good&id={{row.ID}}">Интересно</a></td>
                    <td><a href="/add_label?label=maybe&id={{row.ID}}">Возможно</a></td>
                    <td><a href="/add_label?label=never&id={{row.ID}}">Не интересно</a></td>
                </tr>	
            %end
        </table>
    <a id="last_link" href="/update_news">I Wanna more HACKER NEWS!</a>
    </body>
</html>