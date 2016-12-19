module.exports = function (grunt) {
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    var fs = require('fs');
    function getFilesRule(css_rule, js_rule, use_uglify, use_cssmin, ignore_font) {
        var root = __dirname + "/bower_components";
        use_uglify = use_uglify || false;
        use_cssmin = use_cssmin || false;
        ignore_font = ignore_font || false;
        var res = [], files = fs.readdirSync(root);
        files.forEach(function (file) {
            var pathname = root + '/' + file
                , stat = fs.lstatSync(pathname);
            if (stat.isDirectory()) {
                if (css_rule.length > 0){
                    if (use_cssmin == false){
                        res.push({expand: true, cwd: 'bower_components/' + file, src: css_rule, dest: 'vendor/' + file, flatten: true, filter: 'isFile'});
                    } else {
                        res.push({expand: true, cwd: 'bower_components/' + file, src: css_rule, dest: 'vendor/' + file, flatten: true, filter: 'isFile', ext: '.min.css'});
                    }
                }
                if (js_rule.length > 0){
                    if (use_uglify == false){
                        res.push({expand: true, cwd: 'bower_components/' + file, src: js_rule, dest: 'vendor/' + file, flatten: true, filter: 'isFile'});
                    } else {
                        res.push({expand: true, cwd: 'bower_components/' + file, src: js_rule, dest: 'vendor/' + file, flatten: true, filter: 'isFile', ext: '.min.js'});
                    }
                }
                if (ignore_font === false){
                    res.push({expand: true, src: ['bower_components/' + file + '**/fonts/**'], dest: 'vendor/fonts', flatten: true, filter: 'isFile'});
                }
            }
        });
        return res
    }

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        copy: {
            main: {
                files: getFilesRule(
                    [
                        '**/*.min.css',
                        '**/*.min.css.map'
                    ], [
                        '**/jquery.blueimp-gallery.min.js',
                        '**/jquery.min.map',
                        '**/*.min.js',
                        '**/*.min.js.map'
                    ]
                )
            },
            prism: {
                files: getFilesRule(['**/prism*.css'], ['**/prism*.js'], false, false, true)
            }
        },
        uglify: {
            main: {
                options: {
                    // 設定壓縮後檔頭要插入的註解
                    banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
                    // 使用 SourceMap 並且將 JS Source 與 Map 檔案放在一起
                    sourceMap: true,
                    sourceMapIncludeSources: true
                },
                files: getFilesRule([],
                    [
                        '**/brace-fold.js',
                        '**/codemirror.js',
                        '**/mode/css/css.js',
                        '**/mode/htmlmixed/htmlmixed.js',
                        '**/mode/javascript/javascript.js',
                        '**/message*.js',
                        '**/keymaster.js',
                        '**/instantclick.js',
                        '!*.min.js'
                    ]
                    , true, false, true)
            }
        },
        cssmin: {
            minify: {
                files: getFilesRule(
                    [
                        '**/jquery.steps.css',
                        '**/codemirror.css',
                        '!*.min.css'
                    ], [], false, true, true
                )
            }
        }
    });

    grunt.registerTask('c', ['copy:main']);
    grunt.registerTask('prism', ['copy:prism']);
    grunt.registerTask('js', ['uglify:main']);
    grunt.registerTask('css', ['cssmin:minify']);
    grunt.registerTask('default', ['uglify:main', 'cssmin:minify', 'copy:main']);
};