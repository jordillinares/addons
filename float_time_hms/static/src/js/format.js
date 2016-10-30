openerp.float_time_hms = function(instance){


    var format_value = function( value){
                var pattern = '%02d:%02d:%02d';
                if (value < 0) {
                    value = Math.abs(value);
                    pattern = '-' + pattern;
                }
                var hour = Math.floor(value);
                var min = (value % 1) * 60;
                min = Math.round((min + 0.0001)*1000)/1000;
                if (min >= 60){
                    min = 0;
                    hour = hour + 1;
                }
                sec = (min % 1) * 60;
                sec = Math.round((sec + .0001)*10000)/10000;
                if (sec >= 60){
                    sec = 0;
                    min = min + 1;
                }
                return _.str.sprintf(pattern, hour, min, sec);
    }


    instance.web_kanban.KanbanRecord.include({
           kanban_float_time: function(value) {
		return format_value(value);
	    },
    });
    original_format_value = instance.web.format_value;
    instance.web.format_value = function (value, descriptor, value_if_empty) {
        switch (descriptor.widget || descriptor.type || (descriptor.field && descriptor.field.type)) {
            case 'float_time':
                return format_value(value);
        }
        return original_format_value(value, descriptor, value_if_empty);
    };

    original_parse_value = instance.web.parse_value;
    instance.web.parse_value = function (value, descriptor, value_if_empty) {
        switch (descriptor.widget || descriptor.type || (descriptor.field && descriptor.field.type)) {
            case 'float_time':
                var factor = 1;
                if (value[0] === '-') {
                    value = value.slice(1);
                    factor = -1;
                }
                var float_time_triad = value.split(":");
                if (float_time_triad.length != 3)
                    return factor * original_parse_value(value, {type: "float"});
                var hours = original_parse_value(float_time_triad[0], {type: "integer"});
                var minutes = original_parse_value(float_time_triad[1], {type: "integer"});
                var seconds = original_parse_value(float_time_triad[2], {type: "integer"});
                return factor * (hours + (minutes / 60) + (seconds / 3600) + .0001);
        }
        return original_parse_value(value, descriptor, value_if_empty);
    };

};
