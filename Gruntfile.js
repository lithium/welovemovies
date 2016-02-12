var browserSync = require("browser-sync");

module.exports = function(grunt) {
    grunt.initConfig({
        srcPath: 'breakdown/scss/',
        destPath: 'breakdown/static/',

        pkg: grunt.file.readJSON('package.json'),

        env: {
            dist: {
                NODE_ENV: 'production'
            }
        },

        watch: {
            options:{
                spawn: false,
                livereload: true
            },
            scss: {
                files: ['<%= srcPath %>**/*.scss'],
                tasks: ['sass', 'autoprefixer', 'bs-inject']
            },
            staticFiles: {
                files: ['**/*.html'],
                tasks: ['bs-inject']
            }
        },

        sass: {
            dist: {
                options: {
                    style: 'nested'
                }, 
                files: {
                    '<%= destPath %>css/screen.css': '<%= srcPath %>screen.scss'
                }
            }
        },

        autoprefixer: {
            dist: {
                src: '<%= destPath %>css/screen.css'
            },
            options: {
                map: true
            }
        }
    });

    grunt.registerTask("bs-init", function () {
        var done = this.async();
        browserSync({
            proxy: 'localhost:8000' // This needs to match your current server eg. localhost:5000
        }, function (err, bs) {
            done();
        });
    });

    grunt.registerTask("bs-inject", function () {
        browserSync.reload(['**/*.html','**/*.css']);
    });

    grunt.loadNpmTasks('grunt-autoprefixer');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-env');
    grunt.loadNpmTasks('grunt-shell-spawn');
    grunt.loadNpmTasks('grunt-inline');

    grunt.registerTask('default', ['bs-init', 'sass', 'autoprefixer', 'watch']);
    grunt.registerTask('dist', ['env:dist', 'sass', 'autoprefixer']);
};