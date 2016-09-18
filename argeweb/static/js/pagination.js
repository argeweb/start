$(function(){
    "use strict";

    // Set-up

    //adds params to a link
    var add_params = function(link, params){
        var glue = link.indexOf('?') === -1 ? '?':'&';
        return link + glue + $.param(params);
    };

    // Check if we have localStorage, if not, return, otherwise hide the single paginator.
    if (typeof(localStorage) == 'undefined') return;
    $('.paging-container .single-pager').hide(); //hide the single pager, we don't need it  anymore.
    $('.paging-container .pagination').show();

    var cursors_list = [];
    var current_page = 0;
    var next_page = 0;

    //get cursor list
    if(paging_config.cursor){
        var stored_val = localStorage.getItem(paging_config.storage_key);
        if(stored_val){
            cursors_list = stored_val.split(',');
        }

        //something is wrong so reset to page 1
        if(!cursors_list){
            document.location.replace(paging_config.uri);
            return;
        }
    } else {
        return;
    }

    //see if we've already got the cursor for the current page, if not add it.
    current_page = cursors_list.indexOf(paging_config.cursor);

    if(current_page === -1){
        cursors_list.push(paging_config.cursor);
        current_page = cursors_list.length-1;
    }

    // More less the same thing with the next cursor.
    if(paging_config.next_cursor){
        next_page = cursors_list.indexOf(paging_config.next_cursor);
        if(current_page === -1){
            cursors_list.push(paging_config.next_cursor);
            next_page = cursors_list.length-1;
        }
    }

    //configure next link
    if(!next_page){
        $('.pagination .next').addClass('disabled');
    } else {
        $('.paging-next-link').attr('href',
            add_params(paging_config.uri, {'cursor': cursors_list[next_page], 'limit': paging_config.limit})
        );
    }

    //configure prev link
    if(current_page === 0){
        $('.pagination .previous').addClass('disabled');
    } else {
        var prev_link_params = {
            cursor: cursors_list[current_page-1],
            limit: paging_config.limit
        };
        $('.paging-previous-link').attr('href', add_params(paging_config.uri, prev_link_params) );
    }

    //display result count text
    if(paging_config.results > 0){
        var start_index = current_page * paging_config.limit;
        var end_index = start_index + paging_config.results;
        $('.paging_text').text((start_index+1) + ' to ' + end_index);
    }

});
