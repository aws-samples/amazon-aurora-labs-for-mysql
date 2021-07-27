/*
 * grunt-pack::zip
 * https://github.com/jussi-kalliokoski/grunt-pack
 *
 * Copyright (c) 2012 Jussi Kalliokoski
 * Licensed under the MIT license.
*/

module.exports = function(grunt) {
	var path = require('path')
	var log = grunt.log

	grunt.registerMultiTask('zip', 'Packs files or folders into a .zip', function () {
		var self = this
		var done = this.async()
		var cwd = this.data.cwd || '.'
		var files = grunt.file.expand(this.file.src).map(function (p) {
			return path.relative(cwd, p)
		})

		var args = {
			cmd: 'zip',
			args: ['-r', path.relative(cwd, this.file.dest)]
				.concat(files)
		}

		if (this.data.cwd) {
			args.opts = {
				cwd: cwd
			}
		}

		grunt.utils.spawn(args, function (err, result) {
			if (err) {
				log.error(err)
				return done(false)
			}

			log.success('zip (' + self.file.dest + '): done.')
			done()
		})
	})
}
