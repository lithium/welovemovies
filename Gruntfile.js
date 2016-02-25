
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
        },

        curl: {
            '<%= destPath %>css/font-awesome.min.css': "https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css",
            '<%= destPath %>fonts/fontawesome-webfont.tff': "https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/fonts/fontawesome-webfont.ttf",
            '<%= destPath %>fonts/fontawesome-webfont.woff': "https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/fonts/fontawesome-webfont.woff",
            '<%= destPath %>fonts/fontawesome-webfont.woff2': "https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/fonts/fontawesome-webfont.woff2",

            '<%= destPath %>css/tether.min.css': "https://cdnjs.cloudflare.com/ajax/libs/tether/1.1.1/css/tether.min.css",
            '<%= destPath %>css/bootstrap.min.css': "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.2/css/bootstrap.min.css",
            '<%= destPath %>css/pikaday.min.css': "https://cdnjs.cloudflare.com/ajax/libs/pikaday/1.4.0/css/pikaday.min.css",

            '<%= destPath %>js/jquery.min.js': "https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js",
            '<%= destPath %>js/tether.min.js': "https://cdnjs.cloudflare.com/ajax/libs/tether/1.1.1/js/tether.min.js",
            '<%= destPath %>js/bootstrap.min.js': "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.2/js/bootstrap.min.js",
            '<%= destPath %>js/moment.min.js': "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.11.2/moment.min.js",
            '<%= destPath %>js/list.min.js': "https://raw.githubusercontent.com/javve/list.js/v1.1.1/dist/list.js",

            '<%= destPath %>js/d3.v3.min.js': "http://d3js.org/d3.v3.min.js",
            '<%= destPath %>js/cal-heatmap.min.js': "https://raw.githubusercontent.com/wa0x6e/cal-heatmap/3.5.3/cal-heatmap.js",
            '<%= destPath %>css/cal-heatmap.min.css': "https://raw.githubusercontent.com/wa0x6e/cal-heatmap/3.5.3/cal-heatmap.css",
        }
    });

    grunt.loadNpmTasks('grunt-autoprefixer');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-env');
    grunt.loadNpmTasks('grunt-shell-spawn');
    grunt.loadNpmTasks('grunt-inline');
    grunt.loadNpmTasks('grunt-curl');

    grunt.registerTask('default', ['sass', 'autoprefixer', 'watch']);
    grunt.registerTask('dist', ['env:dist', 'sass', 'curl', 'autoprefixer']);
};