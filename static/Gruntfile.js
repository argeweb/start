module.exports = function (grunt) {
    grunt.loadNpmTasks('grunt-contrib-copy');
    var fs = require('fs');
    function getAllFiles(root, css_rule, js_rule, ignore_font) {
        ignore_font = ignore_font || false;
        var res = [], files = fs.readdirSync(root);
        files.forEach(function (file) {
            var pathname = root + '/' + file
                , stat = fs.lstatSync(pathname);
            if (stat.isDirectory()) {
                res.push({expand: true, cwd: 'bower_components/' + file, src: css_rule, dest: 'vendor/' + file, flatten: true, filter: 'isFile'});
                res.push({expand: true, cwd: 'bower_components/' + file, src: js_rule, dest: 'vendor/' + file, flatten: true, filter: 'isFile'});
                if (ignore_font === false){
                    res.push({expand: true, src: ['bower_components/' + file + '**/fonts/**'], dest: 'vendor/fonts', flatten: true, filter: 'isFile'});
                }
            }
        });
        return res
    }

    var css_rule = [
        '**/jquery.steps.css',
        '**/codemirror.css',
        '**/*.min.css'
    ];
    var js_rule = [
        '**/brace-fold.js',
        '**/codemirror.js',
        '**/css.js',
        '**/htmlmixed.js',
        '**/javascript.js',
        '**/message*.js',
        '**/keymaster.js',
        '**/*.min.js',
        '**/*.min.js.map'
    ];
    var files_rule = getAllFiles(__dirname + "/bower_components", css_rule, js_rule);
    var files_rule_with_prism = getAllFiles(__dirname + "/bower_components", ['**/prism*.css'], ['**/prism*.js'], true);

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        copy: {
            main: {
                files: files_rule
            },
            prism: {
                files: files_rule_with_prism
            }
        }
    });

    grunt.registerTask('prism', ['copy:prism']);
    grunt.registerTask('default', ['copy:main']);
};