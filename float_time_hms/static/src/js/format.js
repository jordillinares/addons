openerp.float_time_hms = function(instance){

	//var module = instance.web // loading the namespace of the 'sample' module
    
    //module.include({
		


		var _t = instance.web._t;
		
		var normalize_format = function (format) {
		    return Date.normalizeFormat(instance.web.strip_raw_chars(format));
		};
	
	
    	instance.web.format_value = function (value, descriptor, value_if_empty) {
    	    // If NaN value, display as with a `false` (empty cell)
    	    if (typeof value === 'number' && isNaN(value)) {
    	        value = false;
    	    }
    	    //noinspection FallthroughInSwitchStatementJS
    	    switch (value) {
    	        case '':
    	            if (descriptor.type === 'char' || descriptor.type === 'text') {
    	                return '';
    	            }
    	            console.warn('Field', descriptor, 'had an empty string as value, treating as false...');
    	            return value_if_empty === undefined ?  '' : value_if_empty;
    	        case false:
    	        case undefined:
    	        case Infinity:
    	        case -Infinity:
    	            return value_if_empty === undefined ?  '' : value_if_empty;
    	    }
    	    var l10n = _t.database.parameters;
    	    switch (descriptor.widget || descriptor.type || (descriptor.field && descriptor.field.type)) {
    	        case 'id':
    	            return value.toString();
    	        case 'integer':
    	            return instance.web.insert_thousand_seps(
    	                _.str.sprintf('%d', value));
    	        case 'float':
    	            var digits = descriptor.digits ? descriptor.digits : [69,2];
    	            digits = typeof digits === "string" ? py.eval(digits) : digits;
    	            var precision = digits[1];
    	            var formatted = _.str.sprintf('%.' + precision + 'f', value).split('.');
    	            formatted[0] = instance.web.insert_thousand_seps(formatted[0]);
    	            return formatted.join(l10n.decimal_point);
    	        case 'float_time':
    	            var pattern = '%02d:%02d:%02d';
    	            if (value < 0) {
    	                value = Math.abs(value);
    	                pattern = '-' + pattern;
    	            }
    	            var hour = Math.floor(value);
    	            var min = Math.floor(Math.round((value % 1) * 60));
    	            var sec = Math.round((((value % 1) * 60) % 1) * 60);
    	            if (sec == 60){
    	                sec = 0;
    	                min = min + 1;
    	            }
    	            if (min == 60){
    	                min = 0;
    	                hour = hour + 1;
    	            }
    	            return _.str.sprintf(pattern, hour, min, sec);
    	        case 'many2one':
    	            // name_get value format
    	            return value[1] ? value[1].split("\n")[0] : value[1];
    	        case 'one2many':
    	        case 'many2many':
    	            if (typeof value === 'string') {
    	                return value;
    	            }
    	            return _.str.sprintf(_t("(%d records)"), value.length);
    	        case 'datetime':
    	            if (typeof(value) == "string")
    	                value = instance.web.auto_str_to_date(value);

    	            return value.toString(normalize_format(l10n.date_format)
    	                        + ' ' + normalize_format(l10n.time_format));
    	        case 'date':
    	            if (typeof(value) == "string")
    	                value = instance.web.str_to_date(value.substring(0,10));
    	            return value.toString(normalize_format(l10n.date_format));
    	        case 'time':
    	            if (typeof(value) == "string")
    	                value = instance.web.auto_str_to_date(value);
    	            return value.toString(normalize_format(l10n.time_format));
    	        case 'selection': case 'statusbar':
    	            // Each choice is [value, label]
    	            if(_.isArray(value)) {
    	                 return value[1];
    	            }
    	            var result = _(descriptor.selection).detect(function (choice) {
    	                return choice[0] === value;
    	            });
    	            if (result) { return result[1]; }
    	            return;
    	        default:
    	            return value;
    	    }
    	};

    	instance.web.parse_value = function (value, descriptor, value_if_empty) {
    	    var date_pattern = normalize_format(_t.database.parameters.date_format),
    	        time_pattern = normalize_format(_t.database.parameters.time_format);
    	    switch (value) {
    	        case false:
    	        case "":
    	            return value_if_empty === undefined ?  false : value_if_empty;
    	    }
    	    var tmp;
    	    switch (descriptor.widget || descriptor.type || (descriptor.field && descriptor.field.type)) {
    	        case 'integer':
    	            do {
    	                tmp = value;
    	                value = value.replace(instance.web._t.database.parameters.thousands_sep, "");
    	            } while(tmp !== value);
    	            tmp = Number(value);
    	            // do not accept not numbers or float values
    	            if (isNaN(tmp) || tmp % 1)
    	                throw new Error(_.str.sprintf(_t("'%s' is not a correct integer"), value));
    	            return tmp;
    	        case 'float':
    	            tmp = Number(value);
    	            if (!isNaN(tmp))
    	                return tmp;

    	            var tmp2 = value;
    	            do {
    	                tmp = tmp2;
    	                tmp2 = tmp.replace(instance.web._t.database.parameters.thousands_sep, "");
    	            } while(tmp !== tmp2);
    	            var reformatted_value = tmp.replace(instance.web._t.database.parameters.decimal_point, ".");
    	            var parsed = Number(reformatted_value);
    	            if (isNaN(parsed))
    	                throw new Error(_.str.sprintf(_t("'%s' is not a correct float"), value));
    	            return parsed;
    	        case 'float_time':
    	            var factor = 1;
    	            if (value[0] === '-') {
    	                value = value.slice(1);
    	                factor = -1;
    	            }
    	            var float_time_triad = value.split(":");
    	            if (float_time_triad.length != 3)
    	                return factor * instance.web.parse_value(value, {type: "float"});
    	            var hours = instance.web.parse_value(float_time_triad[0], {type: "integer"});
    	            var minutes = instance.web.parse_value(float_time_triad[1], {type: "integer"});
    	            var seconds = instance.web.parse_value(float_time_triad[2], {type: "integer"});
    	            return factor * (hours + (minutes / 60) + (seconds / 3600));
    	        case 'progressbar':
    	            return instance.web.parse_value(value, {type: "float"});
    	        case 'datetime':
    	            var datetime = Date.parseExact(
    	                    value, (date_pattern + ' ' + time_pattern));
    	            if (datetime !== null)
    	                return instance.web.datetime_to_str(datetime);
    	            datetime = Date.parseExact(value.toString().replace(/\d+/g, function(m){
    	                return m.length === 1 ? "0" + m : m ;
    	            }), (date_pattern + ' ' + time_pattern));
    	            if (datetime !== null)
    	                return instance.web.datetime_to_str(datetime);
    	            datetime = Date.parse(value);
    	            if (datetime !== null)
    	                return instance.web.datetime_to_str(datetime);
    	            throw new Error(_.str.sprintf(_t("'%s' is not a correct datetime"), value));
    	        case 'date':
    	            var date = Date.parseExact(value, date_pattern);
    	            if (date !== null)
    	                return instance.web.date_to_str(date);
    	            date = Date.parseExact(value.toString().replace(/\d+/g, function(m){
    	                return m.length === 1 ? "0" + m : m ;
    	            }), date_pattern);
    	            if (date !== null)
    	                return instance.web.date_to_str(date);
    	            date = Date.parse(value);
    	            if (date !== null)
    	                return instance.web.date_to_str(date);
    	            throw new Error(_.str.sprintf(_t("'%s' is not a correct date"), value));
    	        case 'time':
    	            var time = Date.parseExact(value, time_pattern);
    	            if (time !== null)
    	                return instance.web.time_to_str(time);
    	            time = Date.parse(value);
    	            if (time !== null)
    	                return instance.web.time_to_str(time);
    	            throw new Error(_.str.sprintf(_t("'%s' is not a correct time"), value));
    	    }
    	    return value;
    	};
    //});
};