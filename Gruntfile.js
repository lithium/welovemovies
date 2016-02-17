
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
                tasks: ['sass', 'autoprefixer']
            },
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

    grunt.loadNpmTasks('grunt-autoprefixer');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-env');
    grunt.loadNpmTasks('grunt-shell-spawn');
    grunt.loadNpmTasks('grunt-inline');

    grunt.registerTask('default', ['sass', 'autoprefixer', 'watch']);
    grunt.registerTask('dist', ['env:dist', 'sass', 'autoprefixer']);
};