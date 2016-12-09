module.exports = function (grunt) {
    grunt.loadNpmTasks('grunt-contrib-copy');
    var fs = require('fs');
    function getAllFiles(root) {
        var res = [], files = fs.readdirSync(root);
        files.forEach(function (file) {
            var pathname = root + '/' + file
                , stat = fs.lstatSync(pathname);
            if (stat.isDirectory()) {
                res.push({expand: true, cwd: 'bower_components/' + file, src: [
                    '**/jquery.steps.css',
                    '**/codemirror.css'
                ], dest: 'vendor/' + file, flatten: true, filter: 'isFile'});
                res.push({expand: true, cwd: 'bower_components/' + file, src: [
                    '**/brace-fold.js',
                    '**/codemirror.js',
                    '**/css.js',
                    '**/htmlmixed.js',
                    '**/javascript.js',
                    '**/message*.js',
                    '**/keymaster.js',
                    '**/*.min.js',
                    '**/*.min.js.map'
                ], dest: 'vendor/' + file, flatten: true, filter: 'isFile'});
                res.push({expand: true, src: ['bower_components/' + file + '**/fonts/**'], dest: 'vendor/fonts', flatten: true, filter: 'isFile'});
            }
        });
        return res
    }
    var files_rule = getAllFiles(__dirname+"/bower_components");

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        copy: {
            main: {
                files: files_rule
            }
        }
    });

    grunt.registerTask('default', ['copy']);
};