/*
 * grunt-pack::tar
 * https://github.com/jussi-kalliokoski/grunt-pack
 *
 * Copyright (c) 2012 Jussi Kalliokoski
 * Licensed under the MIT license.
*/

module.exports = function(grunt) {
	var path = require('path')
	var log = grunt.log

	grunt.registerMultiTask('tar', 'Packs files or folders into a .tar.gz', function () {
		var self = this
		var done = this.async()
		var cwd = this.data.cwd || '.'
		var files = grunt.file.expand(this.file.src).map(function (p) {
			return path.relative(cwd, p)
		})

		var args = {
			cmd: 'tar',
			args: ['pczf', path.relative(cwd, this.file.dest)]
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

			log.success('tar (' + self.file.dest + '): done.')
			done()
		})
	})
}
