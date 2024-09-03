/** @odoo-module */

// Disable right-click
/**document.addEventListener("contextmenu",function(inspect_disable){
inspect_disable.preventDefault();
});*/

document.onkeydown = function(e)

{
    if(event.keyCode == 123)
    {
        return false;
    }

    if (e.ctrlKey && e.shiftKey && e.keyCode == 'I'.charCodeAt(0))
    {
        return false;
    }

    if (e.ctrlKey && e.shiftKey && e.keyCode == 'J'.charCodeAt(0))
    {
        return false;
    }
    
    if (e.ctrlKey && e.shiftKey && e.keyCode == 'E'.charCodeAt(0))
    {
        return false;
    }

    if (e.ctrlKey && e.keyCode == 'U'.charCodeAt(0))
    {
        return false;
    }
   
    if (e.ctrlKey && e.keyCode == 'I'.charCodeAt(0))
    {
        return false;
    }
    
    if (e.ctrlKey && e.keyCode == 'K'.charCodeAt(0))
    {
        return false;
    }

    if (e.ctrlKey && e.shiftKey && e.keyCode == 'C'.charCodeAt(0))
    {
        return false;
    }
};

